#!/bin/bash

# OpenResty AIProxy 启动脚本

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
OPENRESTY_BIN="/usr/local/openresty/bin/openresty"
CONFIG_FILE="$SCRIPT_DIR/conf/nginx.conf"
PID_FILE="$SCRIPT_DIR/logs/nginx.pid"

# 检查OpenResty是否已安装
if [ ! -f "$OPENRESTY_BIN" ]; then
    echo "错误: OpenResty未安装或路径不正确: $OPENRESTY_BIN"
    exit 1
fi

# 检查配置文件是否存在
if [ ! -f "$CONFIG_FILE" ]; then
    echo "错误: 配置文件不存在: $CONFIG_FILE"
    exit 1
fi

# 检查是否已经运行
if [ -f "$PID_FILE" ]; then
    PID=$(cat "$PID_FILE")
    if ps -p "$PID" > /dev/null 2>&1; then
        echo "OpenResty AIProxy已在运行 (PID: $PID)"
        exit 1
    else
        echo "清理旧的PID文件"
        rm -f "$PID_FILE"
    fi
fi

# 创建日志目录
mkdir -p "$SCRIPT_DIR/logs"

# 测试配置文件
echo "测试OpenResty配置..."
"$OPENRESTY_BIN" -t -c "$CONFIG_FILE" -p "$SCRIPT_DIR"
if [ $? -ne 0 ]; then
    echo "配置文件测试失败"
    exit 1
fi

# 启动OpenResty
echo "启动OpenResty AIProxy..."
"$OPENRESTY_BIN" -c "$CONFIG_FILE" -p "$SCRIPT_DIR"

# 检查启动状态
sleep 2
if [ -f "$PID_FILE" ]; then
    PID=$(cat "$PID_FILE")
    if ps -p "$PID" > /dev/null 2>&1; then
        echo "OpenResty AIProxy启动成功"
        echo "代理服务运行在端口: 8001"
        echo "统计页面: http://localhost:8001/stats"
        echo "配置文件: $CONFIG_FILE"
        echo "日志目录: $SCRIPT_DIR/logs"
        echo "PID: $PID"
    else
        echo "OpenResty AIProxy启动失败"
        exit 1
    fi
else
    echo "OpenResty AIProxy启动失败 - 未找到PID文件"
    exit 1
fi 