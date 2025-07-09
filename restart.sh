#!/bin/bash

# OpenResty AIProxy 重启脚本

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

echo "重启OpenResty AIProxy..."

# 停止服务
"$SCRIPT_DIR/stop.sh"

# 等待确保完全停止
sleep 2

# 启动服务
"$SCRIPT_DIR/start.sh" 