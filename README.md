# AIProxy

基于OpenResty的高性能AI API代理服务，支持多渠道路由、API Key管理、WebSocket代理、统计监控等功能。

## 主要特性

- **高性能代理**: 基于OpenResty/Nginx的高并发代理服务
- **多渠道支持**: 支持阿里云百炼、Google Gemini等多个AI服务商
- **智能路由**: 基于Proxy-Key的动态渠道路由
- **WebSocket支持**: 完整支持WebSocket协议代理
- **API Key管理**: 灵活的API Key替换和管理机制
- **统计监控**: 实时统计和可视化仪表板
- **Lua扩展**: 强大的Lua脚本扩展能力

## 系统架构

```
用户请求 → OpenResty → Lua脚本处理 → 目标AI服务
         ↓
    统计记录 → 仪表板展示
```

## 目录结构

```
AIProxy/
├── conf/                    # OpenResty配置和Lua模块
│   ├── nginx.conf          # 主配置文件
│   ├── channels_config.json # 渠道配置
│   ├── api_keys.json       # API Key配置
│   ├── init.lua            # 初始化模块
│   ├── enhanced_api_key_replace.lua # 增强版API Key替换模块
│   ├── record_stats.lua    # 统计记录模块
│   ├── stats_page.lua      # JSON统计API
│   └── stats_dashboard.lua # HTML仪表板
├── logs/                   # 日志目录
├── test/                   # 测试文件
├── docs/                   # 文档目录
├── start.sh               # 启动脚本
├── stop.sh                # 停止脚本
└── restart.sh             # 重启脚本
```

## 快速开始

### 1. 配置设置

首次使用需要设置配置文件：

```bash
# 复制配置模板
cp conf/channels_config.json.example conf/channels_config.json
cp conf/api_keys.json.example conf/api_keys.json

# 编辑配置文件，填入真实的API密钥
vim conf/channels_config.json
vim conf/api_keys.json
```

**重要**: 请参考 [配置指南](docs/配置指南.md) 获取详细的配置说明。

### 2. 启动服务

```bash
# 启动服务
./start.sh

# 重启服务
./restart.sh

# 停止服务
./stop.sh
```

### 3. 访问统计页面

- **JSON API**: http://localhost:8001/stats
- **HTML仪表板**: http://localhost:8001/dashboard

### 4. 使用API代理

```bash
# 使用百炼渠道
curl -X POST http://localhost:8001/chat/completions \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer sk-bailian-tester-001" \
  -d '{"model":"qwen-plus","messages":[{"role":"user","content":"Hello"}]}'

# 使用Gemini渠道
curl -X POST http://localhost:8001/chat/completions \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer sk-bailian-tester-003" \
  -d '{"model":"gemini-pro","messages":[{"role":"user","content":"Hello"}]}'
```

## 配置说明

### 渠道配置 (channels_config.json)

```json
{
  "channels": {
    "bailian": {
      "name": "阿里云百炼",
      "api_url": "https://dashscope.aliyuncs.com",
      "status": "active"
    },
    "gemini": {
      "name": "Google Gemini",
      "api_url": "https://generativelanguage.googleapis.com",
      "status": "active"
    }
  }
}
```

### API Key配置 (api_keys.json)

```json
[
  {
    "proxy_key": "sk-bailian-tester-001",
    "channel": "bailian",
    "status": "active",
    "description": "张三的代理密钥"
  }
]
```

## 功能特性

### 🚀 智能路由
- 基于Proxy-Key自动识别目标渠道
- 动态API URL和请求头设置
- 支持路径重写和参数转换

### 📊 统计监控
- 实时请求统计（成功/失败/响应时间）
- 协议类型统计（HTTP/WebSocket）
- 渠道级别统计
- 可配置自动刷新仪表板

### 🔌 WebSocket支持
- 完整的WebSocket协议代理
- 自动协议检测和切换
- WebSocket连接统计

### ⚡ 高性能
- 基于OpenResty的异步非阻塞架构
- Lua脚本高效处理
- 支持高并发连接

## 开发说明

### 添加新渠道

1. 在 `channels_config.json` 中添加渠道配置
2. 在 `api_keys.json` 中添加对应的API Key
3. 如需特殊处理，修改 `enhanced_api_key_replace.lua`

### 自定义统计

修改 `record_stats.lua` 和 `stats_dashboard.lua` 来添加自定义统计指标。

### 测试

```bash
# 运行集成测试
cd test
python -m pytest integration/ -v
```

## 系统要求

- OpenResty 1.19+
- Lua 5.1+
- macOS/Linux

## 许可证

MIT License

## 贡献

欢迎提交Issue和Pull Request来改进项目。
