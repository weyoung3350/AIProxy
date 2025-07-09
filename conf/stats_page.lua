-- 统计页面模块
-- 显示系统统计信息，包括HTTP和WebSocket协议统计

local cjson = require "cjson"

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

local function get_stats()
    local stats = ngx.shared.stats
    if not stats then
        return {error = "统计数据不可用"}
    end
    
    -- 基础统计
    local total_requests = stats:get("total_requests") or 0
    local successful_requests = stats:get("successful_requests") or 0
    local failed_requests = stats:get("failed_requests") or 0
    local start_time = stats:get("start_time") or ngx.time()
    local last_request_time = stats:get("last_request_time") or 0
    local total_response_time = stats:get("total_response_time") or 0
    
    -- 协议类型统计
    local http_requests = stats:get("http_requests") or 0
    local websocket_requests = stats:get("websocket_requests") or 0
    local websocket_connections = stats:get("websocket_connections") or 0
    
    -- 渠道统计 - 从配置文件动态读取渠道列表
    local channel_stats = {}
    local channels_config = load_channels_config()
    if channels_config then
        for channel_id, channel_info in pairs(channels_config) do
            local channel_key = "channel_" .. channel_info.name .. "_requests"
            local channel_requests = stats:get(channel_key) or 0
            if channel_requests > 0 then
                channel_stats[channel_id] = {
                    name = channel_info.name,
                    requests = channel_requests,
                    status = channel_info.status
                }
            end
        end
    end
    
    -- 计算平均响应时间
    local avg_response_time = "0.000"
    if total_requests > 0 and total_response_time > 0 then
        avg_response_time = string.format("%.3f", total_response_time / total_requests)
    end
    
    -- 计算成功率
    local success_rate = "0.00%"
    if total_requests > 0 then
        success_rate = string.format("%.2f%%", (successful_requests / total_requests) * 100)
    end
    
    -- 计算运行时间
    local uptime_seconds = ngx.time() - start_time
    
    -- WebSocket连接率
    local websocket_connection_rate = "0.00%"
    if websocket_requests > 0 then
        websocket_connection_rate = string.format("%.2f%%", (websocket_connections / websocket_requests) * 100)
    end
    
    return {
        service = "AIProxy",
        version = "2.0.0",
        uptime_seconds = uptime_seconds,
        
        -- 请求统计
        total_requests = total_requests,
        successful_requests = successful_requests,
        failed_requests = failed_requests,
        success_rate = success_rate,
        
        -- 协议统计
        protocol_stats = {
            http_requests = http_requests,
            websocket_requests = websocket_requests,
            websocket_connections = websocket_connections,
            websocket_connection_rate = websocket_connection_rate
        },
        
        -- 渠道统计
        channel_stats = channel_stats,
        
        -- 性能统计
        avg_response_time = avg_response_time,
        last_request_time = last_request_time,
        
        -- API Keys统计
        api_keys_count = #(_G.api_keys or {}),
        
        -- 时间戳
        timestamp = ngx.time()
    }
end

-- 设置响应头
ngx.header["Content-Type"] = "application/json; charset=utf-8"
ngx.header["Access-Control-Allow-Origin"] = "*"

-- 输出统计信息
local stats_data = get_stats()
ngx.say(cjson.encode(stats_data)) 