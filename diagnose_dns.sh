#!/bin/bash

echo "=== AIProxy DNS 诊断脚本 ==="
echo "时间: $(date)"
echo

echo "1. 检查系统DNS配置"
echo "===================="
echo "DNS服务器配置:"
cat /etc/resolv.conf
echo

echo "2. 测试DNS解析"
echo "=============="
echo "测试 dashscope.aliyuncs.com 解析:"
nslookup dashscope.aliyuncs.com
echo

echo "使用8.8.8.8 DNS服务器测试:"
nslookup dashscope.aliyuncs.com 8.8.8.8
echo

echo "使用114.114.114.114 DNS服务器测试:"
nslookup dashscope.aliyuncs.com 114.114.114.114
echo

echo "3. 网络连通性测试"
echo "=================="
echo "Ping测试 dashscope.aliyuncs.com:"
ping -c 3 dashscope.aliyuncs.com
echo

echo "4. 端口连通性测试"
echo "=================="
echo "测试HTTPS端口 (443):"
timeout 5 telnet dashscope.aliyuncs.com 443 || echo "连接失败或超时"
echo

echo "5. OpenResty DNS配置检查"
echo "======================="
echo "当前OpenResty配置中的DNS设置:"
grep -n "resolver" conf/nginx.conf
echo

echo "6. 建议的解决方案"
echo "=================="
echo "如果DNS解析失败，请尝试以下解决方案:"
echo
echo "方案1: 更新DNS服务器"
echo "sudo echo 'nameserver 8.8.8.8' >> /etc/resolv.conf"
echo "sudo echo 'nameserver 114.114.114.114' >> /etc/resolv.conf"
echo
echo "方案2: 使用hosts文件"
echo "echo '8.141.25.100 dashscope.aliyuncs.com' >> /etc/hosts"
echo
echo "方案3: 更新OpenResty DNS配置"
echo "在nginx.conf中添加或修改resolver配置:"
echo "resolver 8.8.8.8 114.114.114.114 valid=300s;"
echo
echo "完成后重启OpenResty: ./restart.sh"
echo

echo "=== 诊断完成 ===" 