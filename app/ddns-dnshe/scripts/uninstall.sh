
#!/bin/bash

set -e

# 停止服务

/mnt/app/ddns-dnshe/scripts/stop.sh

# 删除安装目录

rm -rf /mnt/app/ddns-dnshe

echo "✅ DNSHE DDNS卸载成功！"

