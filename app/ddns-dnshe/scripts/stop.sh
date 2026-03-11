
#!/bin/bash

set -e

DATA_DIR="/mnt/data/ddns-dnshe"

PID_FILE="${DATA_DIR}/ddns.pid"



if [ -f ${PID_FILE} ]; then

    PID=$(cat ${PID_FILE})

    if ps -p ${PID} > /dev/null; then

        kill ${PID}

        rm -f ${PID_FILE}

        echo "✅ DNSHE DDNS已停止"

    else

        rm -f ${PID_FILE}

        echo "ℹ️ DNSHE DDNS未运行（清理残留PID）"

    fi

else

    echo "ℹ️ DNSHE DDNS未运行"

fi

