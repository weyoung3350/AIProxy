-- 统计仪表板模块
-- 显示系统统计信息的HTML仪表板

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

-- 格式化运行时间
local function format_uptime(seconds)
    local days = math.floor(seconds / 86400)
    local hours = math.floor((seconds % 86400) / 3600)
    local minutes = math.floor((seconds % 3600) / 60)
    local secs = seconds % 60
    
    if days > 0 then
        return string.format("%d天 %d小时 %d分钟", days, hours, minutes)
    elseif hours > 0 then
        return string.format("%d小时 %d分钟", hours, minutes)
    elseif minutes > 0 then
        return string.format("%d分钟 %d秒", minutes, secs)
    else
        return string.format("%d秒", secs)
    end
end

-- 格式化时间戳
local function format_timestamp(timestamp)
    if timestamp == 0 then
        return "从未"
    end
    return os.date("%Y-%m-%d %H:%M:%S", timestamp)
end

-- 获取统计数据
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
    
    -- 渠道统计
    local channel_stats = {}
    local channels_config = load_channels_config()
    if channels_config then
        for channel_id, channel_info in pairs(channels_config) do
            local channel_key = "channel_" .. channel_info.name .. "_requests"
            local channel_requests = stats:get(channel_key) or 0
            channel_stats[channel_id] = {
                name = channel_info.name,
                requests = channel_requests,
                status = channel_info.status
            }
        end
    end
    
    -- 计算统计值
    local avg_response_time = "0.000"
    if total_requests > 0 and total_response_time > 0 then
        avg_response_time = string.format("%.3f", total_response_time / total_requests)
    end
    
    local success_rate = 0
    if total_requests > 0 then
        success_rate = (successful_requests / total_requests) * 100
    end
    
    local uptime_seconds = ngx.time() - start_time
    
    local websocket_connection_rate = 0
    if websocket_requests > 0 then
        websocket_connection_rate = (websocket_connections / websocket_requests) * 100
    end
    
    return {
        service = "AIProxy",
        version = "2.0.0",
        uptime_seconds = uptime_seconds,
        uptime_formatted = format_uptime(uptime_seconds),
        
        total_requests = total_requests,
        successful_requests = successful_requests,
        failed_requests = failed_requests,
        success_rate = success_rate,
        
        http_requests = http_requests,
        websocket_requests = websocket_requests,
        websocket_connections = websocket_connections,
        websocket_connection_rate = websocket_connection_rate,
        
        channel_stats = channel_stats,
        
        avg_response_time = avg_response_time,
        last_request_time = last_request_time,
        last_request_formatted = format_timestamp(last_request_time),
        
        api_keys_count = #(_G.api_keys or {}),
        timestamp = ngx.time(),
        timestamp_formatted = format_timestamp(ngx.time())
    }
end

-- 生成HTML页面
local function generate_html(stats)
    local html = [[
<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>AIProxy 统计仪表板</title>
    <style>
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }
        
        body {
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
            padding: 20px;
        }
        
        .container {
            max-width: 1200px;
            margin: 0 auto;
        }
        
        .header {
            text-align: center;
            color: white;
            margin-bottom: 30px;
        }
        
        .header h1 {
            font-size: 2.5rem;
            margin-bottom: 10px;
        }
        
        .header p {
            font-size: 1.1rem;
            opacity: 0.9;
        }
        
        .nav-links {
            text-align: center;
            margin-bottom: 20px;
        }
        
        .nav-links a {
            color: white;
            text-decoration: none;
            margin: 0 15px;
            padding: 8px 16px;
            border: 1px solid rgba(255,255,255,0.3);
            border-radius: 20px;
            transition: all 0.3s ease;
        }
        
        .nav-links a:hover {
            background: rgba(255,255,255,0.1);
        }
        
        .refresh-control {
            text-align: center;
            margin-bottom: 20px;
        }
        
        .refresh-control label {
            color: white;
            margin-right: 10px;
            font-weight: 500;
        }
        
        .refresh-control select {
            padding: 6px 12px;
            border: 1px solid rgba(255,255,255,0.3);
            border-radius: 6px;
            background: rgba(255,255,255,0.1);
            color: white;
            font-size: 14px;
            margin-right: 15px;
        }
        
        .refresh-control select option {
            background: #333;
            color: white;
        }
        
        .refresh-status {
            color: rgba(255,255,255,0.8);
            font-size: 14px;
            margin-left: 10px;
        }
        
        .grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
            gap: 20px;
            margin-bottom: 20px;
        }
        
        .card {
            background: white;
            border-radius: 12px;
            padding: 25px;
            box-shadow: 0 8px 32px rgba(0,0,0,0.1);
            backdrop-filter: blur(10px);
        }
        
        .card h3 {
            color: #333;
            margin-bottom: 20px;
            font-size: 1.3rem;
            border-bottom: 2px solid #667eea;
            padding-bottom: 10px;
        }
        
        .stat-item {
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin-bottom: 15px;
            padding: 10px;
            background: #f8f9fa;
            border-radius: 8px;
        }
        
        .stat-label {
            font-weight: 500;
            color: #555;
        }
        
        .stat-value {
            font-weight: bold;
            color: #333;
        }
        
        .status-active {
            color: #28a745;
        }
        
        .status-inactive {
            color: #dc3545;
        }
        
        .progress-bar {
            width: 100%;
            height: 8px;
            background: #e9ecef;
            border-radius: 4px;
            overflow: hidden;
            margin-top: 5px;
        }
        
        .progress-fill {
            height: 100%;
            background: linear-gradient(90deg, #28a745, #20c997);
            transition: width 0.3s ease;
        }
        
        .refresh-info {
            text-align: center;
            color: white;
            margin-top: 20px;
            opacity: 0.8;
        }
        
        .large-number {
            font-size: 1.8rem;
            font-weight: bold;
            color: #667eea;
        }
        
        .channel-table {
            width: 100%;
            border-collapse: collapse;
            margin-top: 10px;
        }
        
        .channel-table th,
        .channel-table td {
            padding: 12px;
            text-align: left;
            border-bottom: 1px solid #e9ecef;
        }
        
        .channel-table th {
            background: #f8f9fa;
            font-weight: 600;
            color: #495057;
            font-size: 0.9rem;
        }
        
        .channel-table td {
            color: #333;
        }
        
        .channel-table tr:hover {
            background: #f8f9fa;
        }
        
        @media (max-width: 768px) {
            .grid {
                grid-template-columns: 1fr;
            }
            
            .header h1 {
                font-size: 2rem;
            }
            
            .channel-table th,
            .channel-table td {
                padding: 8px;
                font-size: 0.9rem;
            }
        }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>]] .. stats.service .. [[ 统计仪表板</h1>
            <p>版本 ]] .. stats.version .. [[ | 运行时间: ]] .. stats.uptime_formatted .. [[</p>
        </div>
        
        <div class="nav-links">
            <a href="/dashboard">仪表板</a>
            <a href="/stats">JSON API</a>
        </div>
        
        <div class="refresh-control">
            <label for="refreshInterval">自动刷新:</label>
            <select id="refreshInterval">
                <option value="0">不刷新</option>
                <option value="5" selected>5秒</option>
                <option value="10">10秒</option>
                <option value="15">15秒</option>
                <option value="30">30秒</option>
                <option value="60">60秒</option>
            </select>
            <span class="refresh-status" id="refreshStatus">下次刷新: 5秒</span>
        </div>
        
        <div class="grid">
            <!-- 系统信息 -->
            <div class="card">
                <h3>系统信息</h3>
                <div class="stat-item">
                    <span class="stat-label">服务名称</span>
                    <span class="stat-value">]] .. stats.service .. [[</span>
                </div>
                <div class="stat-item">
                    <span class="stat-label">版本</span>
                    <span class="stat-value">]] .. stats.version .. [[</span>
                </div>
                <div class="stat-item">
                    <span class="stat-label">运行时间</span>
                    <span class="stat-value">]] .. stats.uptime_formatted .. [[</span>
                </div>
                <div class="stat-item">
                    <span class="stat-label">API密钥数量</span>
                    <span class="stat-value">]] .. stats.api_keys_count .. [[</span>
                </div>
                <div class="stat-item">
                    <span class="stat-label">最后更新</span>
                    <span class="stat-value">]] .. stats.timestamp_formatted .. [[</span>
                </div>
            </div>
            
            <!-- 请求统计 -->
            <div class="card">
                <h3>请求统计</h3>
                <div class="stat-item">
                    <span class="stat-label">总请求数</span>
                    <span class="stat-value large-number">]] .. stats.total_requests .. [[</span>
                </div>
                <div class="stat-item">
                    <span class="stat-label">成功请求</span>
                    <span class="stat-value status-active">]] .. stats.successful_requests .. [[</span>
                </div>
                <div class="stat-item">
                    <span class="stat-label">失败请求</span>
                    <span class="stat-value status-inactive">]] .. stats.failed_requests .. [[</span>
                </div>
                <div class="stat-item">
                    <span class="stat-label">成功率</span>
                    <span class="stat-value">]] .. string.format("%.2f%%", stats.success_rate) .. [[</span>
                </div>
                <div class="progress-bar">
                    <div class="progress-fill" style="width: ]] .. stats.success_rate .. [[%"></div>
                </div>
                <div class="stat-item">
                    <span class="stat-label">平均响应时间</span>
                    <span class="stat-value">]] .. stats.avg_response_time .. [[秒</span>
                </div>
                <div class="stat-item">
                    <span class="stat-label">最后请求时间</span>
                    <span class="stat-value">]] .. stats.last_request_formatted .. [[</span>
                </div>
            </div>
            
            <!-- 协议统计 -->
            <div class="card">
                <h3>协议统计</h3>
                <div class="stat-item">
                    <span class="stat-label">HTTP请求</span>
                    <span class="stat-value">]] .. stats.http_requests .. [[</span>
                </div>
                <div class="stat-item">
                    <span class="stat-label">WebSocket请求</span>
                    <span class="stat-value">]] .. stats.websocket_requests .. [[</span>
                </div>
                <div class="stat-item">
                    <span class="stat-label">WebSocket连接</span>
                    <span class="stat-value">]] .. stats.websocket_connections .. [[</span>
                </div>
                <div class="stat-item">
                    <span class="stat-label">WebSocket连接率</span>
                    <span class="stat-value">]] .. string.format("%.2f%%", stats.websocket_connection_rate) .. [[</span>
                </div>
                <div class="progress-bar">
                    <div class="progress-fill" style="width: ]] .. stats.websocket_connection_rate .. [[%"></div>
                </div>
            </div>
            
            <!-- 渠道统计 -->
            <div class="card">
                <h3>渠道统计</h3>
                <table class="channel-table">
                    <thead>
                        <tr>
                            <th>渠道名称</th>
                            <th>请求数</th>
                            <th>状态</th>
                        </tr>
                    </thead>
                    <tbody>]]
    
    -- 动态生成渠道统计表格行
    for channel_id, channel_data in pairs(stats.channel_stats) do
        local status_class = channel_data.status == "active" and "status-active" or "status-inactive"
        local status_text = channel_data.status == "active" and "活跃" or "非活跃"
        
        html = html .. [[
                        <tr>
                            <td>]] .. channel_data.name .. [[</td>
                            <td>]] .. channel_data.requests .. [[</td>
                            <td class="]] .. status_class .. [[">]] .. status_text .. [[</td>
                        </tr>]]
    end
    
    html = html .. [[
                    </tbody>
                </table>
            </div>
        </div>
        
        <div class="refresh-info">
            <p>当前时间: ]] .. stats.timestamp_formatted .. [[</p>
        </div>
    </div>
    
    <script>
        let refreshTimer = null;
        let countdownTimer = null;
        let remainingTime = 0;
        
        // 从本地存储加载刷新间隔设置
        function loadRefreshInterval() {
            const saved = localStorage.getItem('dashboardRefreshInterval');
            return saved ? parseInt(saved) : 5;
        }
        
        // 保存刷新间隔设置到本地存储
        function saveRefreshInterval(interval) {
            localStorage.setItem('dashboardRefreshInterval', interval.toString());
        }
        
        // 更新刷新状态显示
        function updateRefreshStatus(interval, remaining = 0) {
            const statusElement = document.getElementById('refreshStatus');
            if (interval === 0) {
                statusElement.textContent = '自动刷新已关闭';
            } else if (remaining > 0) {
                statusElement.textContent = `下次刷新: ${remaining}秒`;
            } else {
                statusElement.textContent = `每${interval}秒自动刷新`;
            }
        }
        
        // 开始倒计时
        function startCountdown(interval) {
            if (interval === 0) return;
            
            remainingTime = interval;
            updateRefreshStatus(interval, remainingTime);
            
            countdownTimer = setInterval(() => {
                remainingTime--;
                if (remainingTime > 0) {
                    updateRefreshStatus(interval, remainingTime);
                } else {
                    clearInterval(countdownTimer);
                    window.location.reload();
                }
            }, 1000);
        }
        
        // 设置自动刷新
        function setAutoRefresh(interval) {
            // 清除现有的定时器
            if (refreshTimer) {
                clearTimeout(refreshTimer);
                refreshTimer = null;
            }
            if (countdownTimer) {
                clearInterval(countdownTimer);
                countdownTimer = null;
            }
            
            if (interval > 0) {
                // 设置新的刷新定时器
                refreshTimer = setTimeout(() => {
                    window.location.reload();
                }, interval * 1000);
                
                // 开始倒计时显示
                startCountdown(interval);
            } else {
                updateRefreshStatus(0);
            }
            
            // 保存设置
            saveRefreshInterval(interval);
        }
        
        // 页面加载完成后初始化
        document.addEventListener('DOMContentLoaded', function() {
            // 加载保存的刷新间隔设置
            const savedInterval = loadRefreshInterval();
            const selectElement = document.getElementById('refreshInterval');
            selectElement.value = savedInterval;
            
            // 设置初始刷新
            setAutoRefresh(savedInterval);
            
            // 监听下拉框变化
            selectElement.addEventListener('change', function() {
                const newInterval = parseInt(this.value);
                setAutoRefresh(newInterval);
            });
            
            // 添加页面加载动画
            const cards = document.querySelectorAll('.card');
            cards.forEach((card, index) => {
                card.style.opacity = '0';
                card.style.transform = 'translateY(20px)';
                setTimeout(() => {
                    card.style.transition = 'opacity 0.5s ease, transform 0.5s ease';
                    card.style.opacity = '1';
                    card.style.transform = 'translateY(0)';
                }, index * 100);
            });
        });
    </script>
</body>
</html>]]
    
    return html
end

-- 设置响应头
ngx.header["Content-Type"] = "text/html; charset=utf-8"
ngx.header["Access-Control-Allow-Origin"] = "*"

-- 获取统计数据并生成HTML页面
local stats_data = get_stats()
if stats_data.error then
    ngx.say("<html><body><h1>错误: " .. stats_data.error .. "</h1></body></html>")
else
    ngx.say(generate_html(stats_data))
end 