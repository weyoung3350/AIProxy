-- 统计记录模块
-- 记录请求统计信息，支持HTTP和WebSocket协议

local function record_request_stats()
    local stats = ngx.shared.stats
    if not stats then
        ngx.log(ngx.ERR, "统计共享字典未初始化")
        return
    end
    
    -- 检查是否为内部管理页面，如果是则跳过统计
    local uri = ngx.var.uri
    if uri == "/stats" or uri == "/dashboard" or uri == "/favicon.ico" then
        ngx.log(ngx.DEBUG, "内部管理页面请求，跳过统计记录: " .. uri)
        return
    end
    
    -- 获取基本信息
    local status = ngx.status
    local request_time = ngx.var.request_time or 0
    local protocol_type = ngx.ctx.is_websocket and "WebSocket" or "HTTP"
    local channel_name = ngx.ctx.channel_name or "unknown"
    
    -- 更新总请求数
    local total_requests = stats:get("total_requests") or 0
    stats:set("total_requests", total_requests + 1)
    
    -- 更新协议类型统计
    local http_requests = stats:get("http_requests") or 0
    local websocket_requests = stats:get("websocket_requests") or 0
    
    if ngx.ctx.is_websocket then
        stats:set("websocket_requests", websocket_requests + 1)
        
        -- WebSocket连接统计
        if status == 101 then -- WebSocket握手成功
            local websocket_connections = stats:get("websocket_connections") or 0
            stats:set("websocket_connections", websocket_connections + 1)
            ngx.log(ngx.INFO, "WebSocket连接建立成功")
        end
    else
        stats:set("http_requests", http_requests + 1)
    end
    
    -- 更新成功/失败统计
    if status >= 200 and status < 400 then
        local successful_requests = stats:get("successful_requests") or 0
        stats:set("successful_requests", successful_requests + 1)
    else
        local failed_requests = stats:get("failed_requests") or 0
        stats:set("failed_requests", failed_requests + 1)
    end
    
    -- 更新渠道统计
    if channel_name ~= "unknown" then
        local channel_key = "channel_" .. channel_name .. "_requests"
        local channel_requests = stats:get(channel_key) or 0
        stats:set(channel_key, channel_requests + 1)
    end
    
    -- 更新响应时间统计
    local total_response_time = stats:get("total_response_time") or 0
    local new_total_time = total_response_time + tonumber(request_time)
    stats:set("total_response_time", new_total_time)
    
    -- 记录最后请求时间
    stats:set("last_request_time", ngx.time())
    
    -- 记录日志
    ngx.log(ngx.INFO, "记录请求统计: 协议=" .. protocol_type .. 
            ", 渠道=" .. channel_name .. 
            ", 状态=" .. status .. 
            ", 耗时=" .. request_time)
end

record_request_stats() 