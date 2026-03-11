
#!/bin/bash

set -e

DATA_DIR="/mnt/data/ddns-dnshe"

PID_FILE="${DATA_DIR}/ddns.pid"



if [ -f ${PID_FILE} ]; then

    PID=$(cat ${PID_FILE})

    if ps -p ${PID} > /dev/null; then

        echo "🟢 运行中（PID：${PID}）"

        exit 0

    else

        rm -f ${PID_FILE}

        echo "🔴 已停止（清理残留PID）"

        exit 1

    fi

else

    echo "🔴 已停止"

    exit 1

fi

