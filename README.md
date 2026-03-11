# DNSHE DDNS -  DNSHE动态域名更新工具

一个专为DNSHE设计的  动态域名更新工具，支持 IPv6 地址自动检测和更新。

## ✨ 功能特性

- 🌐 **DNSHE API 集成** - 使用 DNSHE API 管理子域名和 DNS记录
- 🚀 **IPv6 支持** - 仅支持 IPv6 地址检测和 AAAA 记录更新
- 🎨 **Web 管理界面** - 美观的后台管理系统，支持配置管理和实时监控
- 📊 **实时日志** - 查看 DDNS服务运行状态和日志
- ⚙️ **灵活配置** - 支持自定义检查间隔、TTL 等参数
- 🔧 **一键控制** - 启动、停止、重启服务
- 🚀 **自动获取域名 ID** - 根据 API Key 自动获取子域名列表，无需手动查找

## 📦 项目结构

```
dnshe-ddns/
├── app/ddns-dnshe/          # DDNS 核心程序
│   ├── app/
│   │   ├── ddns_dnshe.py    # DDNS 主程序
│   │   └── ddns_config.ini  # 配置文件模板
│   ├── scripts/             # 服务控制脚本
│   │   ├── install.sh
│   │   ├── start.sh
│   │   ├── stop.sh
│   │   ├── status.sh
│   │   └── uninstall.sh
│   └── app.json             # 应用描述文件
├── ddns_web.py              # Web 后台主程序
├── static_script.js         # Web 后台前端脚本
├── start_web.sh             # Web 后台启动脚本
├── stop_web.sh              # Web 后台停止脚本
└── docs/                    # 文档目录
```

## 🚀 快速开始

### 1. 安装 DDNS服务

```bash
# 进入应用目录
cd app/ddns-dnshe

# 运行安装脚本
sudo bash scripts/install.sh

# 启动服务
bash scripts/start.sh
```

### 2. 启动 Web 后台

```bash
# 启动 Web 后台
bash start_web.sh

# 访问后台管理界面
# http://localhost:5000/
```

### 3. 配置参数

在 Web 后台中配置以下参数：
- **API Key**: DNSHE API 密钥
- **API Secret**: DNSHE API 密钥
- **Subdomain ID**: 子域名 ID（可点击"🔍 自动获取"按钮自动获取）
- **TTL**: DNS TTL（秒）

💡 **提示**：如果不知道 Subdomain ID，可以点击输入框旁边的"自动获取"按钮，系统会自动获取你的所有子域名！

## 📋 系统要求

- Python 3.6+
- Flask (Web 后台依赖)
- Requests
- Linux 系统

## 🔧 使用说明

### DDNS服务管理

```bash
# 启动服务
bash scripts/start.sh

# 停止服务
bash scripts/stop.sh

# 重启服务
bash scripts/stop.sh && bash scripts/start.sh

# 查看状态
bash scripts/status.sh
```

### Web 后台管理

```bash
# 启动 Web 后台
bash start_web.sh

# 停止 Web 后台
bash stop_web.sh

# 查看日志
tail -f ddns_web.log
```

## 🌐 API接口

本项目使用 DNSHE API：
- **API地址**: https://api005.dnshe.com/index.php?m=domain_hub
- **认证方式**: HTTP Headers (X-API-Key, X-API-Secret)
- **支持的端点**:
  - `subdomains` - 子域名管理
  - `dns_records` - DNS记录管理
  - `quota` - 配额查询

## 📝 配置文件

配置文件位置：`app/ddns-dnshe/app/ddns_config.ini`

```ini
[DNSHE]
api_key = your_api_key
api_secret = your_api_secret
subdomain_id = your_subdomain_id
ttl = 600

[DDNS]
check_interval = 600
dns_ttl = 600
auto_renew = True
```

## 💡 功能说明

### IPv6 检测
- 使用 api64.ipify.org 等 API 获取公网 IPv6 地址
- 仅检测和更新 AAAA 记录
- 不支持 IPv4 更新

### Web 后台功能
- ✅ 服务状态监控
- ✅ 配置参数管理
- ✅ 实时日志查看
- ✅ 一键启动/停止/重启
- ✅ API连接测试

## 📖 常见问题

### 1. 如何获取 API Key？
登录 DNSHE 官网，在个人中心获取 API Key 和 Secret。

### 2. Subdomain ID 在哪里查看？
在 Web 后台点击"测试 API连接"按钮，会自动获取子域名列表和 ID。

### 3. 为什么只支持 IPv6？
本项目设计为仅支持 IPv6，如需 IPv4 支持请自行修改代码。

## �� License

MIT License

## 👥 作者

gaowenbin

## 🙏 致谢

感谢 DNSHE 提供的 API 服务
感谢 LINGMA 全程编写 本人一点没参与 
