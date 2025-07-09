#!/bin/bash

# OpenResty AIProxy 停止脚本

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PID_FILE="$SCRIPT_DIR/logs/nginx.pid"

# 检查是否正在运行
if [ ! -f "$PID_FILE" ]; then
    echo "OpenResty AIProxy未运行"
    exit 0
fi

PID=$(cat "$PID_FILE")

# 检查进程是否存在
if ! ps -p "$PID" > /dev/null 2>&1; then
    echo "OpenResty AIProxy进程不存在，清理PID文件"
    rm -f "$PID_FILE"
    exit 0
fi

# 停止服务
echo "停止OpenResty AIProxy (PID: $PID)..."
kill "$PID"

# 等待进程退出
for i in {1..10}; do
    if ! ps -p "$PID" > /dev/null 2>&1; then
        echo "OpenResty AIProxy已停止"
        rm -f "$PID_FILE"
        exit 0
    fi
    sleep 1
done

# 如果进程仍然存在，强制杀死
echo "强制停止OpenResty AIProxy..."
kill -9 "$PID" 2>/dev/null
rm -f "$PID_FILE"
echo "OpenResty AIProxy已强制停止" 