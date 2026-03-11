
#!/bin/bash

set -e

APP_ROOT="/mnt/app/ddns-dnshe"

# 创建数据目录（日志/运行状态）

mkdir -p /mnt/data/ddns-dnshe/logs

chmod 755 /mnt/data/ddns-dnshe/logs

# 赋予脚本执行权限

chmod +x ${APP_ROOT}/scripts/*.sh

chmod 600 ${APP_ROOT}/app/ddns_config.ini

# 安装Python依赖

if command -v pip3 &>/dev/null; then

    pip3 install requests -i https://pypi.tuna.tsinghua.edu.cn/simple --user

else

    apt update && apt install python3-pip -y

    pip3 install requests -i https://pypi.tuna.tsinghua.edu.cn/simple --user

fi

echo "✅ DNSHE DDNS安装成功！请在NAS后台配置后启动。"

