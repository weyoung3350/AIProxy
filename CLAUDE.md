# CLAUDE.md

用中文和我沟通

## 项目概览

AIProxy 是基于 OpenResty/Nginx 的高性能 AI API 代理服务，支持多渠道路由、API 密钥管理、WebSocket 代理和统计监控。它作为阿里云百炼和 Google Gemini 等各种 AI 服务提供商的统一网关。

## 核心架构

- **OpenResty/Nginx**: 高性能反向代理服务器
- **Lua Scripts**: 在 `conf/` 目录中处理业务逻辑
- **Dynamic Routing**: 基于代理密钥将请求路由到不同的 AI 服务渠道
- **WebSocket Support**: 完整的 WebSocket 协议代理功能
- **Statistics**: 实时监控和仪表板

## 常用开发命令

### 服务管理
```bash
# 启动服务
./start.sh

# 停止服务  
./stop.sh

# 重启服务（配置更改后需要）
./restart.sh

# 检查服务状态
ps aux | grep nginx
```

### 测试
```bash
# 运行集成测试
cd test
python -m pytest integration/ -v

# 运行特定测试
python -m pytest integration/test_chat_sdk.py -v

# 安装测试依赖
pip install -r requirements.txt
```

### 配置测试
```bash
# 测试 OpenResty 配置
/usr/local/openresty/bin/openresty -t -c conf/nginx.conf -p .
```

## 关键配置文件

### 核心配置
- `conf/nginx.conf`: 主要 OpenResty 配置
- `conf/channels_config.json`: 渠道路由配置
- `conf/api_keys.json`: API 密钥映射

### Lua 模块
- `conf/init.lua`: 初始化模块
- `conf/enhanced_process.lua`: 增强的 API 密钥替换和路由
- `conf/record_stats.lua`: 统计记录
- `conf/stats_page.lua`: JSON 统计 API
- `conf/stats_dashboard.lua`: HTML 仪表板

## 开发指南

### 配置管理
- 配置更改后始终使用 `./restart.sh` 重启 OpenResty
- 使用提供的示例文件作为模板：
  - `conf/channels_config.json.example`
  - `conf/api_keys.json.example`

### 测试要求
- 使用真实的 API，而不是模拟
- 部署前所有测试必须通过
- 测试 HTTP 和 WebSocket 协议
- 使用 `unittest` 框架进行结构化测试

### Shell 脚本
- 保持 shell 脚本简单，兼容 zsh 和 bash
- 使用清晰、可读的日志消息，不要过多符号
- 始终使用项目的 start.sh/stop.sh/restart.sh 脚本

### Lua 开发
- 遵循 `conf/` 目录中的现有模式
- 使用共享字典 `stats` 进行跨工作进程数据共享
- 处理 HTTP 和 WebSocket 协议
- 实现适当的错误处理和日志记录

## 服务架构

服务运行在端口 443 上，提供：
- `/stats`: JSON 统计 API
- `/dashboard`: HTML 统计仪表板
- `/`: AI API 请求的主要代理端点

## 环境
- **平台**: 使用 Homebrew 安装 OpenResty 的 macOS
- **OpenResty 路径**: `/usr/local/openresty/bin/openresty`
- **服务端口**: 443
- **日志目录**: `/opt/logs/nginx`

## 重要说明

- 任何配置更改后都必须重启服务
- 所有实现必须使用真实的 API，而不是模拟
- WebSocket 连接完全支持，具有适当的超时设置
- 统计数据存储在共享内存中以提高性能
- DNS 解析使用多个服务器以保证可靠性