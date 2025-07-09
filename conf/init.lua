-- OpenResty初始化模块
-- 加载配置和初始化统计数据

local cjson = require "cjson"

-- 初始化统计数据
local stats = ngx.shared.stats
if not stats:get("total_requests") then
    stats:set("total_requests", 0)
    stats:set("successful_requests", 0)
    stats:set("failed_requests", 0)
    stats:set("start_time", ngx.time())
end

-- 加载API Key配置
local function load_api_keys()
    local file = io.open("conf/api_keys.json", "r")
    if not file then
        ngx.log(ngx.ERR, "无法打开API Key配置文件")
        return {}
    end
    
    local content = file:read("*all")
    file:close()
    
    local ok, keys = pcall(cjson.decode, content)
    if not ok then
        ngx.log(ngx.ERR, "API Key配置文件格式错误")
        return {}
    end
    
    return keys
end

-- 全局变量
_G.api_keys = load_api_keys()

ngx.log(ngx.INFO, "OpenResty初始化完成，加载了 " .. #_G.api_keys .. " 个API Key") 