
#!/bin/bash

set -e

APP_ROOT="/mnt/app/ddns-dnshe"

DATA_DIR="/mnt/data/ddns-dnshe"

LOG_FILE="${DATA_DIR}/logs/ddns_dnshe.log"

PID_FILE="${DATA_DIR}/ddns.pid"



# 检查是否已运行

if [ -f ${PID_FILE} ]; then

    PID=$(cat ${PID_FILE})

    if ps -p ${PID} > /dev/null; then

        echo "ℹ️ DNSHE DDNS已运行（PID：${PID}）"

        exit 0

    fi

fi



# 后台启动程序

nohup python3 ${APP_ROOT}/app/ddns_dnshe.py >> ${LOG_FILE} 2>&1 &

echo $! > ${PID_FILE}



echo "✅ DNSHE DDNS启动成功！"

echo "📄 日志路径：${LOG_FILE}"

