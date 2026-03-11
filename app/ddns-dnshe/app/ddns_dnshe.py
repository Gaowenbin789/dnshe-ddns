#!/usr/bin/env python3
import requests
import json
import time
import configparser
import os
import socket
import fcntl
import struct
from datetime import datetime

# 禁用SSL警告
requests.packages.urllib3.disable_warnings()

CONFIG_PATH = '/mnt/app/ddns-dnshe/app/ddns_config.ini'

def load_config():
    """加载配置文件"""
    config = configparser.ConfigParser()
    if not os.path.exists(CONFIG_PATH):
        config['DNSHE'] = {
            'api_key': 'YOUR_API_KEY_HERE',
            'api_secret': 'YOUR_API_SECRET_HERE',
            'subdomain_id': 229726,
            'ttl': 600
        }
        config['SETTINGS'] = {
            'check_interval': 30,
            'log_file': '/mnt/data/ddns-dnshe/logs/ddns.log'
        }
        with open(CONFIG_PATH, 'w') as f:
            config.write(f)
    config.read(CONFIG_PATH, encoding='utf-8')
    return config

def get_local_ipv6():
    """从本地网卡获取公网IPv6（不依赖外部接口）"""
    try:
        # 获取所有网络接口
        interfaces = [i[1] for i in socket.if_nameindex() if i[1] not in ['lo', 'docker0']]
        for ifname in interfaces:
            try:
                # 创建IPv6套接字
                s = socket.socket(socket.AF_INET6, socket.SOCK_DGRAM)
                # 获取接口的IPv6地址
                addr = socket.inet_ntop(socket.AF_INET6, fcntl.ioctl(
                    s.fileno(),
                    0x8919,  # SIOCGIFA6ADDR
                    struct.pack('256s', ifname.encode('utf-8'))
                )[20:28])
                # 过滤内网IPv6（fe80开头是链路本地，::1是回环）
                if not addr.startswith('fe80:') and not addr == '::1':
                    return addr
            except:
                continue
    except Exception as e:
        log(f"本地获取IPv6失败: {str(e)}", "DEBUG")
    return None

def get_public_ipv6():
    """混合方式获取IPv6（先本地，后外部）"""
    # 1. 先从本地网卡获取
    local_ipv6 = get_local_ipv6()
    if local_ipv6:
        log(f"✅ 本地网卡获取IPv6: {local_ipv6}", "INFO")
        return local_ipv6
    
    # 2. 外部接口获取（缩短超时到5秒）
    ipv6_urls = [
        "https://api6.ipify.org",
        "https://ipv6.icanhazip.com",
        "https://ifconfig.me/ipv6",
        "https://api64.ipify.org"
    ]
    log("🔍 本地获取失败，尝试外部接口获取IPv6...", "INFO")
    for url in ipv6_urls:
        try:
            response = requests.get(
                url, 
                timeout=5,  # 缩短超时到5秒
                headers={'User-Agent': 'Mozilla/5.0'},
                verify=False
            )
            ipv6 = response.text.strip()
            if ":" in ipv6 and not ipv6.startswith("fe80:") and not ipv6.startswith("::1"):
                log(f"✅ 外部接口{url}获取IPv6: {ipv6}", "INFO")
                return ipv6
        except Exception as e:
            log(f"❌ 外部接口{url}失败: {str(e)}", "DEBUG")
            continue
    
    log("❌ 所有方式都无法获取IPv6", "ERROR")
    return None

def get_aaaa_record(subdomain_id, config):
    """获取现有AAAA记录"""
    log(f"🔍 检查ID={subdomain_id}的AAAA记录...", "INFO")
    api_key = config['DNSHE']['api_key']
    api_secret = config['DNSHE']['api_secret']
    api_url = "https://api005.dnshe.com/index.php"
    params = {
        'm': 'domain_hub',
        'endpoint': 'dns_records',
        'action': 'list',
        'subdomain_id': subdomain_id
    }
    headers = {
        'X-API-Key': api_key,
        'X-API-Secret': api_secret,
        'User-Agent': 'Mozilla/5.0'
    }
    
    try:
        response = requests.get(
            api_url, 
            params=params, 
            headers=headers, 
            timeout=10,
            verify=False
        )
        if response.status_code == 200:
            data = response.json()
            records = data.get('records', data.get('data', []))
            for rec in records:
                if rec.get('type') == 'AAAA' and rec.get('name') == '@':
                    log(f"✅ 找到现有AAAA记录: {rec['content']}", "INFO")
                    return rec
        log(f"❌ 未找到AAAA记录，返回数据: {data}", "DEBUG")
    except Exception as e:
        log(f"❌ 获取AAAA记录失败: {str(e)}", "ERROR")
    return None

def update_aaaa_record(record_id, new_ipv6, config):
    """更新AAAA记录"""
    log(f"🔄 尝试更新AAAA记录(ID={record_id})到{new_ipv6}...", "INFO")
    api_key = config['DNSHE']['api_key']
    api_secret = config['DNSHE']['api_secret']
    ttl = int(config['DNSHE']['ttl'])
    api_url = "https://api005.dnshe.com/index.php"
    params = {
        'm': 'domain_hub',
        'endpoint': 'dns_records',
        'action': 'update',
        'id': record_id
    }
    headers = {
        'X-API-Key': api_key,
        'X-API-Secret': api_secret,
        'Content-Type': 'application/json',
        'User-Agent': 'Mozilla/5.0'
    }
    payload = {
        'content': new_ipv6,
        'ttl': ttl
    }
    
    try:
        response = requests.post(
            api_url, 
            params=params, 
            headers=headers, 
            json=payload, 
            timeout=10,
            verify=False
        )
        result = response.json()
        if result.get('code') == 0 or result.get('success'):
            log(f"✅ IPv6更新成功: {new_ipv6}", "INFO")
            return True
        else:
            log(f"❌ IPv6更新失败: {result}", "ERROR")
    except Exception as e:
        log(f"❌ 更新AAAA记录异常: {str(e)}", "ERROR")
    return False

def create_aaaa_record(subdomain_id, new_ipv6, config):
    """创建AAAA记录"""
    log(f"➕ 尝试创建AAAA记录(ID={subdomain_id})为{new_ipv6}...", "INFO")
    api_key = config['DNSHE']['api_key']
    api_secret = config['DNSHE']['api_secret']
    ttl = int(config['DNSHE']['ttl'])
    api_url = "https://api005.dnshe.com/index.php"
    params = {
        'm': 'domain_hub',
        'endpoint': 'dns_records',
        'action': 'create'
    }
    headers = {
        'X-API-Key': api_key,
        'X-API-Secret': api_secret,
        'Content-Type': 'application/json',
        'User-Agent': 'Mozilla/5.0'
    }
    payload = {
        'subdomain_id': subdomain_id,
        'type': 'AAAA',
        'content': new_ipv6,
        'ttl': ttl,
        'name': '@'
    }
    
    try:
        response = requests.post(
            api_url, 
            params=params, 
            headers=headers, 
            json=payload, 
            timeout=10,
            verify=False
        )
        result = response.json()
        if result.get('code') == 0 or result.get('success'):
            log(f"✅ IPv6记录创建成功: {new_ipv6}", "INFO")
            return True
        else:
            log(f"❌ IPv6创建失败: {result}", "ERROR")
    except Exception as e:
        log(f"❌ 创建AAAA记录异常: {str(e)}", "ERROR")
    return False

def log(message, level="INFO"):
    """统一日志输出"""
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    log_line = f"[{timestamp}] [{level}] {message}"
    print(log_line)
    log_file = load_config()['SETTINGS']['log_file']
    with open(log_file, 'a', encoding='utf-8') as f:
        f.write(log_line + "\n")

def main():
    """主程序：增加详细日志，修复卡住问题"""
    log("=== DDNS服务启动（固定ID=229726，解析=IPv6）===", "INFO")
    config = load_config()
    check_interval = int(config['SETTINGS']['check_interval'])
    subdomain_id = int(config['DNSHE']['subdomain_id'])
    last_ipv6 = ""
    
    log(f"🔧 配置信息：ID={subdomain_id}，检查间隔={check_interval}秒", "INFO")
    
    while True:
        log("========================================", "INFO")
        log("🔍 开始新一轮IPv6检查...", "INFO")
        
        # 1. 获取公网IPv6（核心修复：先本地后外部）
        current_ipv6 = get_public_ipv6()
        if not current_ipv6:
            log("❌ 无法获取公网IPv6，10秒后重试", "ERROR")
            time.sleep(10)
            continue
        
        # 2. IPv6未变化则跳过
        if current_ipv6 == last_ipv6:
            log(f"ℹ️ IPv6未变化: {current_ipv6}", "INFO")
            time.sleep(check_interval)
            continue
        
        log(f"✅ 检测到新IPv6: {current_ipv6}（上次: {last_ipv6}）", "INFO")
        
        # 3. 检查现有AAAA记录
        aaaa_record = get_aaaa_record(subdomain_id, config)
        
        # 4. 更新/创建IPv6记录
        success = False
        if aaaa_record:
            success = update_aaaa_record(aaaa_record['id'], current_ipv6, config)
        else:
            success = create_aaaa_record(subdomain_id, current_ipv6, config)
        
        # 5. 记录成功的IPv6
        if success:
            last_ipv6 = current_ipv6
        
        # 6. 间隔等待
        log(f"⏳ 等待{check_interval}秒后再次检查...", "INFO")
        time.sleep(check_interval)

if __name__ == "__main__":
    main()
