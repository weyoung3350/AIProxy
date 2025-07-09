# AIProxy 代理服务概要设计文档

## 1. 文档概述

### 1.1 文档目的
本文档旨在为AIProxy代理服务项目提供完整的概要设计规范，包括系统架构、模块设计、接口设计、数据设计等技术实现方案，为开发团队提供技术指导。

### 1.2 项目背景
公司内部用户和产品线需要调用第三方AI平台（如阿里云百炼、OpenAI等）的API接口。出于安全管控考虑，需要实现一个代理服务来统一管理API-Key，避免直接暴露第三方平台的API-Key给用户。

### 1.3 设计原则
- **安全性**：集中管理API-Key，防止泄露
- **可扩展性**：支持多渠道接入和水平扩展
- **高性能**：低延迟的代理转发
- **可维护性**：简化配置管理和运维
- **高兼容性**：支持三方平台SDK或OpenAI SDK接入，支持HTTP、WebSocket、WebRTC

## 2. 系统架构设计

### 2.1 总体架构

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   用户/应用     │    │   代理转发      │    │   第三方AI平台  │
│                 │    │                 │    │                 │
│  ┌───────────┐  │    │  ┌───────────┐  │    │  ┌───────────┐  │
│  │OpenAI SDK │  │───▶│  │ 代理转发  │  │───▶│  │阿里云百炼 │  │
│  └───────────┘  │    │  └───────────┘  │    │  └───────────┘  │
│                 │    │                 │    │                 │
│  ┌───────────┐  │    │  ┌───────────┐  │    │  ┌───────────┐  │
│  │WebSocket  │  │───▶│  │配置管理   │  │───▶│  │OpenAI API │  │
│  │   Client  │  │    │  └───────────┘  │    │  └───────────┘  │
│  └───────────┘  │    │                 │    │                 │
│                 │    │  ┌───────────┐  │    │  ┌───────────┐  │
│  ┌───────────┐  │    │  │统计监控   │  │    │  │其他AI平台 │  │
│  │HTTP Client│  │    │  └───────────┘  │    │  └───────────┘  │
│  └───────────┘  │    │                 │    │                 │
└─────────────────┘    └─────────────────┘    └─────────────────┘
```

### 2.2 核心组件

#### 2.2.1 OpenResty代理层
- **功能**：HTTP/WebSocket/WebRTC协议代理转发
- **职责**：接收用户请求，调用Lua脚本处理，转发到目标渠道
- **特点**：高性能、低延迟、支持负载均衡

#### 2.2.2 Lua脚本处理层
- **功能**：API-Key替换、用户认证、请求路由
- **职责**：核心业务逻辑处理
- **特点**：灵活配置、热重载支持

#### 2.2.3 配置管理层
- **功能**：用户配置、渠道配置、映射关系管理
- **职责**：配置文件读取、解析、缓存
- **特点**：支持热重载、版本控制

#### 2.2.4 统计监控层
- **功能**：使用量统计、性能监控、异常告警
- **职责**：数据收集、分析、报告
- **特点**：实时统计、多维度分析

## 3. 模块设计

### 关键点说明
1. **利用OpenResty做转发代理** OpenResty优秀的代理能力，结合Lua的灵活扩展，不需要自己编写代理逻辑，只需编写Lua脚本即可。
2. **无需关心业务数据**：代理层只处理包头，不解析或干预业务内容，保证通用性和高性能，适配多种AI渠道和协议。
1. **配置热重载**：Lua脚本可定时重新加载配置文件，支持动态变更用户/渠道信息，无需重启服务。
2. **HTTP/WebSocket/WebRTC统一处理**：代理层只需在HTTP请求阶段（包括WebSocket/WebRTC握手）做包头解析和API-Key替换，后续数据帧透明转发，无需区分协议细节。
3. **日志与异常处理**：所有认证失败、Key无效等情况均可在Lua脚本中记录日志，并返回合适的HTTP状态码或错误信息，便于运维和审计。


### 3.1 核心代理模块

#### 3.1.1 HTTP代理模块
```yaml
模块名称: HTTP代理模块
功能描述: 处理HTTP协议的代理转发（本质为统一包头处理与API-Key替换，后续流量透明转发）
主要接口:
  - http_request_handler(): HTTP请求处理入口
  - validate_proxy_key(): Proxy-Key验证
  - replace_api_key(): API-Key替换
  - route_to_channel(): 渠道路由选择
  - forward_request(): 请求转发
核心流程:
  1. 接收HTTP请求
  2. 验证Proxy-Key
  3. 替换为渠道API-Key
  4. 选择目标渠道
  5. 转发请求并返回响应
  6. 仅在包头处理阶段做认证与替换，业务数据透明转发
  7. 由统一Lua脚本实现，无需关心上层业务协议
```

#### 3.1.2 WebSocket/WebRTC代理模块
```yaml
模块名称: WebSocket/WebRTC代理模块
功能描述: 处理WebSocket协议的代理转发（与HTTP一致，握手阶段包头处理，后续数据帧透明转发）
主要接口:
  - websocket_handshake(): WebSocket/WebRTC握手处理
  - websocket_frame_handler(): 数据帧处理
  - connection_manager(): 连接管理
核心流程:
  1. WebSocket/WebRTC握手阶段API-Key替换（与HTTP包头处理一致）
  2. 建立与目标渠道的WebSocket/WebRTC连接
  3. 数据帧透明转发，无需解析业务内容
  4. 连接状态管理
  5. 由统一Lua脚本实现，无需分别开发两套逻辑
```

### 3.2 配置管理模块

#### 3.2.1 配置加载模块
```yaml
模块名称: 配置加载模块
功能描述: 配置文件的加载、解析、缓存
主要接口:
  - load_config(): 配置文件加载
  - parse_config(): 配置文件解析
  - cache_config(): 配置缓存管理
  - reload_config(): 配置热重载
配置类型:
  - API Key配置: api_keys.json
```

**实现方式说明：**
- 通过Lua脚本在初始化时加载JSON配置文件（conf/api_keys.json），包含API Key列表和用户信息。
- 系统启动时一次性加载配置到内存，运行时直接使用内存中的配置数据。
- 配置变更需要编辑JSON文件后重启服务生效。

**伪代码示例：**
```lua
local cjson = require "cjson"

function load_api_keys()
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

-- 初始化时加载
_G.api_keys = load_api_keys()
```

**关键点：**
- 配置在系统初始化时一次性加载到内存。
- 异常处理：加载失败时记录详细错误日志。
- 配置变更需要重启服务生效，简化实现复杂度。

#### 3.2.2 映射关系模块
```yaml
模块名称: 映射关系模块
功能描述: Proxy-Key与渠道API-Key的映射管理
主要接口:
  - get_channel_by_proxy_key(): 根据Proxy-Key获取渠道
  - get_api_key_by_channel(): 根据渠道获取API-Key
  - validate_user_permission(): 用户权限验证
数据结构:
  - proxy_key_mapping: Proxy-Key映射表
  - channel_config: 渠道配置表
  - user_permission: 用户权限表
```

### 3.3 统计监控模块

#### 3.3.1 使用量统计模块
```yaml
模块名称: 使用量统计模块
功能描述: 多维度使用量统计
主要接口:
  - record_request(): 请求记录
  - calculate_statistics(): 统计计算
  - generate_report(): 报告生成
统计维度:
  - 用户维度: 按用户统计使用量
  - 渠道维度: 按渠道统计使用量
  - 时间维度: 按时间统计使用量
  - 接口维度: 按API接口统计使用量
```

**实现方式说明：**
- 本系统统计数据仅保存在内存中。所有统计信息（如请求次数、成功率、响应时间等）在Lua脚本内以table结构实时累加。
- 系统通过定时任务，每隔60秒将当前统计快照序列化为JSON格式，写入本地日志文件（如`stats.log`）。
- 无需实时数据库或外部持久化，简化实现，满足MVP阶段统计需求。

**伪代码示例：**
```lua
local stats = {}

function update_stats(user, channel, status, response_time)
    -- ...累加统计逻辑...
end

function write_stats_log()
    local stats_json = json_encode(stats)
    write_log("stats.log", stats_json)
end

-- 定时任务，每60秒写一次统计日志
function start_stats_timer()
    while true do
        sleep(60)
        write_stats_log()
    end
end

-- 启动时调用
start_stats_timer()
```

**关键点：**
- 统计信息结构化记录，便于后续分析和报表生成。
- 支持多维度统计与异常监控。
- MVP阶段仅用内存+定时日志。监控功能由OpenResty自身提供，无需在本系统中单独设计。

## 4. 接口设计

### 4.1 管理接口设计结构说明

本节描述AIProxy的管理接口（如用户管理、统计查询等）对外暴露方式，分为两种实现方案：
1. **推荐方案：独立管理API服务**（如Flask/FastAPI/Go等，单独进程，安全性高，便于扩展）
2. **MVP可选方案：与代理服务进程集成**（直接在OpenResty+Lua中实现极简管理接口，部署简单，功能有限）

### 4.2 管理接口设计

- 仅实现“MVP可选方案：与代理服务进程集成”，即管理接口直接由OpenResty+Lua脚本处理，详见下述。

#### 4.2.1 管理接口实现（与代理服务进程集成）
- 适用于MVP阶段仅需基础管理台功能、对安全性要求不高的场景。
- 技术实现细节如下：

**a) 路径分流**
- 在OpenResty配置中，将如`/api/v1/users`、`/api/v1/statistics`等管理接口的请求，转发到Lua脚本处理。

**b) Lua脚本内路由与响应**
- 在Lua脚本中判断请求路径，如果是管理接口，则直接读取内存中的配置/统计数据，生成JSON响应返回。
- 可实现GET/POST等简单操作（如只支持GET，或通过POST参数变更内存配置，MVP阶段可不落盘）。

**c) 简单认证**
- 在Lua脚本中校验请求头中的Token，仅允许管理员访问。

**d) 响应格式**
- 直接返回JSON字符串，Content-Type设为application/json。

**e) 伪代码示例**
```lua
function on_request(txn)
    local path = txn.sf:path()
    local method = txn.sf:method()
    local token = txn.sf:req_hdr("Authorization")
    -- 管理接口Token校验
    if token ~= "Bearer admin-secret-token" then
        txn.res:set_status(401)
        txn.res:send('{"error":"Unauthorized"}')
        return
    end
    -- 用户管理接口
    if path == "/api/v1/users" and method == "GET" then
        local users_json = json_encode(CONFIG.users)
        txn.res:set_status(200)
        txn.res:set_header("Content-Type", "application/json")
        txn.res:send(users_json)
        return
    end
    -- 统计查询接口
    if path == "/api/v1/statistics/users" and method == "GET" then
        local stats_json = json_encode(STATS.users)
        txn.res:set_status(200)
        txn.res:set_header("Content-Type", "application/json")
        txn.res:send(stats_json)
        return
    end
    -- 其他流量正常代理
    -- ...原有代理逻辑...
end
```

**f) 优缺点说明**
- 优点：部署简单，无需新进程，MVP阶段可快速实现管理台对接。
- 局限：仅适合“只读”或极简变更（如内存变更），不适合复杂业务。认证机制简单，安全性有限。代码维护性较差，后续建议独立服务化。

## 5. 数据设计

### 5.1 配置文件设计

#### 5.1.1 API Key配置文件 (conf/api_keys.json)
```json
数据结构:
[
  {
    "key": "渠道API-Key",
    "user": "用户标识",
    "channel": "渠道标识",
    "status": "状态(active/disabled)"
  }
]
      
示例:
[
  {
    "key": "sk-aliyun-xxx",
    "user": "张三",
    "channel": "qianwen",
    "status": "active"
  },
  {
    "key": "sk-openai-xxx",
    "user": "李四",
    "channel": "openai",
    "status": "active"
  }
]
```

#### 5.1.2 OpenResty配置文件 (conf/nginx.conf)
```nginx
配置内容:
- 服务器监听端口和域名
- Lua脚本路径配置
- 上游服务器配置
- 代理转发规则
- 日志输出配置
- SSL/TLS配置
      
示例:
server {
    listen 8001;
    server_name localhost;
    
    # 统计页面
    location /stats {
        content_by_lua_file conf/stats_page.lua;
    }
    
    # API代理
    location / {
        access_by_lua_file conf/api_key_replace.lua;
        log_by_lua_file conf/record_stats.lua;
        proxy_pass https://qianwen_api;
    }
}
```

### 5.2 统计数据设计

#### 5.2.1 请求日志数据
```yaml
数据结构:
  request_log:
    timestamp: 请求时间戳
    user_id: 用户ID
    proxy_key: Proxy-Key
    channel_id: 渠道ID
    api_endpoint: API端点
    method: HTTP方法
    status_code: 响应状态码
    response_time: 响应时间
    request_size: 请求大小
    response_size: 响应大小
    error_message: 错误信息
```

#### 5.2.2 统计汇总数据
```yaml
数据结构:
  statistics_summary:
    time_bucket: 时间桶（小时/天/月）
    user_id: 用户ID
    channel_id: 渠道ID
    total_requests: 总请求数
    success_requests: 成功请求数
    failed_requests: 失败请求数
    avg_response_time: 平均响应时间
    total_data_size: 总数据量
```

## 6. 安全设计

### 6.1 认证安全
- **Proxy-Key认证**：基于Bearer Token的认证机制
- **API-Key保护**：渠道API-Key集中管理，用户无法直接访问
- **访问控制**：基于用户权限的渠道访问控制

### 6.2 传输安全
- **HTTPS支持**：所有HTTP通信使用HTTPS加密
- **WSS支持**：WebSocket通信使用WSS加密
- **证书管理**：SSL证书的配置和管理

### 6.3 运维安全
- **访问日志**：完整记录所有API访问日志
- **异常监控**：实时监控异常访问行为
- **配置备份**：定期备份配置文件和统计数据

## 7. 性能设计

### 7.1 性能目标
- **并发处理**：支持100+并发用户
- **响应时间**：代理层延迟 < 100ms
- **吞吐量**：支持1000+ QPS
- **可用性**：99.9%系统可用性

### 7.2 性能优化策略
- **连接池管理**：复用HTTP连接，减少建连开销
- **配置缓存**：内存缓存配置信息，减少文件IO
- **异步处理**：使用异步IO提高并发处理能力
- **负载均衡**：支持多实例部署和负载均衡

### 7.3 性能监控
- **响应时间监控**：实时监控API响应时间
- **吞吐量监控**：监控系统处理能力
- **资源使用监控**：监控CPU、内存、网络使用情况
- **性能告警**：性能指标异常时及时告警

## 8. 可扩展性设计

### 8.1 水平扩展
- **无状态设计**：代理服务设计为无状态，支持水平扩展
- **配置共享**：多实例共享配置文件或配置中心
- **负载均衡**：通过负载均衡器分发请求

### 8.2 功能扩展
- **插件机制**：支持自定义Lua脚本扩展功能
- **渠道扩展**：新渠道接入只需添加配置，无需修改代码
- **协议扩展**：支持新协议的扩展接入

### 8.3 存储扩展
- **配置存储**：从文件存储迁移到数据库存储
- **统计存储**：支持时序数据库存储统计数据
- **日志存储**：支持日志收集和分析系统

## 9. 运维设计

### 9.1 部署运维
- **容器化部署**：支持Docker容器化部署
- **自动化部署**：支持CI/CD自动化部署流程
- **配置管理**：统一的配置管理和版本控制

### 9.2 监控运维
- **健康检查**：提供健康检查接口
- **指标监控**：集成Prometheus等监控系统
- **日志管理**：结构化日志输出，支持日志收集

### 9.3 故障处理
- **故障转移**：支持渠道故障自动转移
- **降级处理**：系统过载时的降级策略
- **恢复机制**：故障恢复后的自动恢复机制

---

**文档版本**：v1.0  
**创建日期**：2025年1月9日  
**最后更新**：2025年1月9日 14:32  
**文档状态**：已审核 

---

**备注：**
后续如需更高安全性和扩展性，可考虑将管理接口独立为专用API服务（如Flask/FastAPI/Go等），实现更完善的权限控制、审计和运维能力。 