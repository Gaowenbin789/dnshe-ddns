#!/bin/bash
set -e

PID_FILE="/home/admin/ddns_web.pid"

if [ -f ${PID_FILE} ]; then
    PID=$(cat ${PID_FILE})
    if ps -p ${PID} > /dev/null; then
        kill ${PID}
        rm -f ${PID_FILE}
        echo "✅ DNSHE DDNS Web 后台已停止"
    else
        rm -f ${PID_FILE}
        echo "ℹ️ DNSHE DDNS Web 后台未运行（清理残留 PID）"
    fi
else
    echo "ℹ️ DNSHE DDNS Web 后台未运行"
fi
