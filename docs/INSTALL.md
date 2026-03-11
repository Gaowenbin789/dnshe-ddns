# DNSHE DDNS 安装指南

## 📋 准备工作

1. 确保已安装 Python 3.6+
2. 确保已安装 pip
3. 获取 DNSHE API Key 和 Secret

## 🔧 安装步骤

### 1. 克隆项目

```bash
git clone https://github.com/YOUR_USERNAME/dnshe-ddns.git
cd dnshe-ddns
```

### 2. 安装依赖

```bash
pip3 install flask requests
```

### 3. 配置 DDNS服务

编辑配置文件：

```bash
cd app/ddns-dnshe/app
nano ddns_config.ini
```

填写你的配置：

```ini
[DNSHE]
api_key = 你的 API Key
api_secret = 你的 API Secret
subdomain_id = 你的子域名 ID
ttl = 600

[DDNS]
check_interval = 600
dns_ttl = 600
auto_renew = True
```

### 4. 安装 DDNS服务

```bash
cd /path/to/dnshe-ddns/app/ddns-dnshe
sudo bash scripts/install.sh
```

### 5. 启动 DDNS服务

```bash
bash scripts/start.sh
```

### 6. 启动 Web 后台

返回项目根目录：

```bash
cd /path/to/dnshe-ddns
bash start_web.sh
```

访问：http://localhost:5000/

## ✅ 验证安装

### 检查 DDNS服务

```bash
bash scripts/status.sh
```

### 检查 Web 后台

```bash
curl http://localhost:5000/api/status
```

### 查看日志

```bash
# DDNS 日志
tail -f /mnt/data/ddns-dnshe/logs/ddns.log

# Web 后台日志
tail -f ddns_web.log
```

## 🔍 故障排除

### 问题 1: 无法启动 DDNS服务

检查配置文件路径是否正确，确保文件存在。

### 问题 2: Web 后台无法访问

检查端口 5000 是否被占用：

```bash
netstat -tlnp | grep 5000
```

### 问题 3: API连接失败

检查网络连接和 API Key/Secret 是否正确。

## 📖 下一步

- 访问 Web 后台管理界面
- 测试 API连接
- 查看实时日志
- 配置自动启动

详细使用说明请查看 [README.md](../README.md)
