-- 架构说明：
-- 1. API-KEY: 渠道的真实密钥，配置在channels_config.json中
-- 2. Proxy-Key: 分发给用户的代理密钥，配置在api_keys.json中
-- 3. 支持HTTP和WebSocket协议
-- 4. 动态代理到不同的目标服务器

local cjson = require "cjson"

-- 检测是否为WebSocket请求
local function is_websocket_request()
    local upgrade = ngx.var.http_upgrade
    local connection = ngx.var.http_connection
    
    if upgrade and string.lower(upgrade) == "websocket" then
        return true
    end
    
    if connection and string.find(string.lower(connection), "upgrade") then
        return true
    end
    
    return false
end

-- 加载渠道配置
local function load_channels_config()
    local file = io.open("conf/channels_config.json", "r")
    if not file then
        ngx.log(ngx.ERR, "无法打开渠道配置文件")
        return nil
    end
    
    local content = file:read("*all")
    file:close()
    
    local ok, config = pcall(cjson.decode, content)
    if not ok then
        ngx.log(ngx.ERR, "渠道配置文件格式错误")
        return nil
    end
    
    return config.channels
end

-- 加载Proxy-Key配置
local function load_proxy_keys_config()
    local file = io.open("conf/api_keys.json", "r")
    if not file then
        ngx.log(ngx.ERR, "无法打开Proxy-Key配置文件")
        return nil
    end
    
    local content = file:read("*all")
    file:close()
    
    local ok, keys = pcall(cjson.decode, content)
    if not ok then
        ngx.log(ngx.ERR, "Proxy-Key配置文件格式错误")
        return nil
    end
    
    return keys
end

-- 根据Proxy-Key查找用户信息
local function find_user_by_proxy_key(proxy_key, proxy_keys)
    if not proxy_keys then
        return nil
    end
    
    for _, proxy_key_info in ipairs(proxy_keys) do
        if proxy_key_info.proxy_key == proxy_key and proxy_key_info.status == "active" then
            return proxy_key_info
        end
    end
    
    return nil
end

-- 根据渠道ID获取渠道配置
local function get_channel_config(channel_id, channels)
    if not channels or not channel_id then
        return nil
    end
    
    local channel = channels[channel_id]
    if channel and channel.status == "active" then
        return channel
    end
    
    return nil
end

-- 设置动态代理目标
local function set_dynamic_proxy(channel_config, is_websocket)
    -- 设置请求头
    ngx.req.set_header("Host", channel_config.host)
    
    local uri = ngx.var.uri
    
    if is_websocket then
        -- WebSocket请求处理
        ngx.log(ngx.INFO, "检测到WebSocket请求: " .. uri)
        
        if not channel_config.supports_websocket then
            ngx.log(ngx.ERR, "渠道不支持WebSocket: " .. (channel_config.name or "unknown"))
            ngx.status = 400
            ngx.say('{"error":"Channel does not support WebSocket"}')
            ngx.exit(400)
            return
        end
        
        -- WebSocket路径重写
        if channel_config.websocket_endpoints and channel_config.websocket_endpoints[uri] then
            ngx.req.set_uri(channel_config.websocket_endpoints[uri])
            ngx.log(ngx.INFO, "WebSocket路径重写: " .. uri .. " -> " .. channel_config.websocket_endpoints[uri])
        end
        
        ngx.log(ngx.INFO, "WebSocket握手处理完成，后续数据帧将透明转发")
    else
        -- HTTP请求路径重写
        if channel_config.path_rewrite then
            -- 遍历路径重写规则，忽略以下划线开头的注释字段
            for from_path, to_path in pairs(channel_config.path_rewrite) do
                if not string.match(from_path, "^_") and from_path == uri then
                    ngx.req.set_uri(to_path)
                    ngx.log(ngx.INFO, "HTTP路径重写: " .. from_path .. " -> " .. to_path)
                    break
                end
            end
        end
    end
    
    -- 动态设置代理目标
    local target_url = is_websocket and channel_config.websocket_url or channel_config.base_url
    ngx.var.proxy_pass_target = target_url
    
    -- 设置SSL SNI
    ngx.var.proxy_ssl_server_name = channel_config.host
    
    -- 设置代理变量
    ngx.ctx.proxy_host = channel_config.host
    ngx.ctx.proxy_url = target_url
    ngx.ctx.channel_name = channel_config.name
    ngx.ctx.is_websocket = is_websocket
    
    ngx.log(ngx.INFO, "动态代理设置完成 - 目标: " .. target_url)
end

-- 主处理函数
local function enhanced_process()
    ngx.log(ngx.INFO, "=== 开始处理API Key替换 ===")
    
    -- 检查是否为内部管理页面，如果是则直接返回，不需要验证
    local uri = ngx.var.uri
    if uri == "/stats" or uri == "/dashboard" then
        ngx.log(ngx.INFO, "内部管理页面请求，跳过API Key验证: " .. uri)
        return
    end
    
    -- 检测请求类型
    local is_websocket = is_websocket_request()
    local protocol_type = is_websocket and "WebSocket" or "HTTP"
    ngx.log(ngx.INFO, "检测到协议类型: " .. protocol_type)
    
    -- 获取当前Authorization头
    local auth_header = ngx.var.http_authorization
    if not auth_header then
        ngx.log(ngx.WARN, "请求中没有Authorization头")
        ngx.status = 401
        ngx.say('{"error":"Missing Authorization header"}')
        ngx.exit(401)
        return
    end
    
    ngx.log(ngx.INFO, "收到Authorization头: " .. string.sub(auth_header, 1, 20) .. "...")
    
    -- 检查是否为Bearer token格式（不区分大小写）
    local bearer_pattern = "^[Bb][Ee][Aa][Rr][Ee][Rr] "
    local bearer_match = string.match(auth_header, bearer_pattern)
    if not bearer_match then
        ngx.log(ngx.WARN, "Authorization头格式不正确")
        ngx.status = 401
        ngx.say('{"error":"Invalid Authorization format"}')
        ngx.exit(401)
        return
    end
    
    -- 提取Proxy-Key（动态计算前缀长度）
    local bearer_prefix_len = string.len(bearer_match)
    local proxy_key = string.sub(auth_header, bearer_prefix_len + 1)
    ngx.log(ngx.INFO, "提取到Proxy-Key: " .. proxy_key)
    
    -- 加载配置
    ngx.log(ngx.INFO, "开始加载配置文件...")
    local channels = load_channels_config()
    local proxy_keys = load_proxy_keys_config()
    
    if not channels or not proxy_keys then
        ngx.log(ngx.ERR, "无法加载配置文件")
        ngx.status = 500
        ngx.say('{"error":"Configuration error"}')
        ngx.exit(500)
        return
    end
    
    ngx.log(ngx.INFO, "配置加载成功 - Proxy-Key数: " .. #proxy_keys)
    
    -- 根据Proxy-Key查找用户信息
    local user_info = find_user_by_proxy_key(proxy_key, proxy_keys)
    if not user_info then
        ngx.log(ngx.WARN, "未找到有效的Proxy-Key: " .. proxy_key)
        ngx.status = 403
        ngx.say('{"error":"Invalid proxy key"}')
        ngx.exit(403)
        return
    end
    
    ngx.log(ngx.INFO, "找到用户信息: " .. (user_info.user or "unknown") .. ", 渠道: " .. (user_info.channel or "unknown"))
    
    -- 获取用户指定的渠道配置
    local channel_config = get_channel_config(user_info.channel, channels)
    if not channel_config then
        ngx.log(ngx.ERR, "用户指定的渠道不可用: " .. (user_info.channel or "unknown"))
        ngx.status = 503
        ngx.say('{"error":"Channel not available"}')
        ngx.exit(503)
        return
    end
    
    ngx.log(ngx.INFO, "使用渠道: " .. (channel_config.name or "unknown"))
    
    -- 使用渠道的真实API-KEY替换Authorization头
    ngx.req.set_header("Authorization", "Bearer " .. channel_config.api_key)
    
    -- 设置动态代理
    set_dynamic_proxy(channel_config, is_websocket)
    
    -- 记录日志
    ngx.log(ngx.INFO, "密钥替换成功 - 协议: " .. protocol_type .. 
            ", 用户: " .. (user_info.user or "unknown") .. 
            " (Proxy-Key: " .. (user_info.proxy_key or "unknown") .. ")" ..
            ", 渠道: " .. (user_info.channel or "unknown") .. 
            " (" .. (channel_config.name or "unknown") .. ")" ..
            ", API-Key: " .. string.sub(channel_config.api_key, 1, 10) .. "...")
            
    ngx.log(ngx.INFO, "=== API Key替换处理完成 ===")
end

enhanced_process() 