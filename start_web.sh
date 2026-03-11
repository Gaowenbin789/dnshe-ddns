#!/bin/bash
set -e

WEB_SCRIPT="/home/admin/ddns_web.py"
PID_FILE="/home/admin/ddns_web.pid"
LOG_FILE="/home/admin/ddns_web.log"

# 检查是否已运行
if [ -f ${PID_FILE} ]; then
    PID=$(cat ${PID_FILE})
    if ps -p ${PID} > /dev/null; then
        echo "ℹ️ DNSHE DDNS Web 后台已运行（PID：${PID}）"
        exit 0
    fi
fi

# 后台启动程序
nohup python3 ${WEB_SCRIPT} >> ${LOG_FILE} 2>&1 &
echo $! > ${PID_FILE}

echo "✅ DNSHE DDNS Web 后台启动成功！"
echo "🌐 访问地址：http://localhost:5000"
echo "📄 Web 日志路径：${LOG_FILE}"
