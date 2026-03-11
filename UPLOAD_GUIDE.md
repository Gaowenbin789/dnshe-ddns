# GitHub 上传指南

## 📦 项目已打包完成

位置：`/home/admin/dnshe-ddns-github/`

## 🚀 上传到 GitHub 的步骤

### 方法一：使用 Git 命令（推荐）

#### 1. 初始化 Git 仓库

```bash
cd /home/admin/dnshe-ddns-github/
git init
```

#### 2. 添加所有文件

```bash
git add .
```

#### 3. 提交更改

```bash
git commit -m "Initial commit: DNSHE DDNS with Web UI"
```

#### 4. 在 GitHub 创建新仓库

访问 https://github.com/new
- 仓库名：dnshe-ddns
- 描述：DNSHE DDNS for Feiniu NAS with Web UI
- 公开或私有：自选
- **不要**勾选"Initialize this repository with a README"

#### 5. 关联远程仓库并推送

```bash
# 关联远程仓库（替换 YOUR_USERNAME 为你的 GitHub 用户名）
git remote add origin https://github.com/YOUR_USERNAME/dnshe-ddns.git

# 推送到 GitHub
git branch -M main
git push -u origin main
```

### 方法二：直接上传 ZIP 文件

#### 1. 打包为 ZIP

```bash
cd /home/admin/
zip -r dnshe-ddns.zip dnshe-ddns-github/
```

生成的文件：`/home/admin/dnshe-ddns.zip`

#### 2. 手动上传到 GitHub

1. 访问 https://github.com/new 创建仓库
2. 创建后点击 "uploading an existing file"
3. 将 ZIP 文件解压后拖拽上传
4. 或者直接使用 Git 命令行

### 方法三：使用 GitHub Desktop

1. 下载并安装 GitHub Desktop
2. 克隆空仓库到本地
3. 将 `dnshe-ddns-github` 中的文件复制到仓库目录
4. 使用 GitHub Desktop 提交并推送

## 📝 上传前检查清单

- [ ] 删除了配置文件中的敏感信息（API Key/Secret）
- [ ] 添加了 .gitignore
- [ ] 添加了 README.md
- [ ] 测试了所有功能正常
- [ ] 代码格式整洁

## 🔒 安全提示

### 不要上传的文件

- ✅ 已添加到 .gitignore：
  - `ddns_config.ini` (包含 API密钥)
  - `*.log` (日志文件)
  - `*.pid` (进程文件)
  - `__pycache__/` (Python缓存)

### 需要手动配置的文件

上传后，用户需要自行创建配置文件：

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

## 📊 推荐的 GitHub 仓库设置

### 1. 添加主题标签

在仓库设置中添加：
- `python`
- `ddns`
- `nas`
- `dns`
- `ipv6`
- `flask`

### 2. 添加许可证

推荐使用 MIT License

### 3. 启用 Issues

允许用户提交问题和功能请求

### 4. 添加 Wiki

用于详细文档

## 🎉 上传成功后的操作

### 1. 更新 README

将 README 中的安装说明更新为：

```bash
git clone https://github.com/YOUR_USERNAME/dnshe-ddns.git
cd dnshe-ddns
```

### 2. 分享项目

- 在相关论坛分享
- 添加到 Awesome 列表
- 社交媒体宣传

### 3. 维护项目

- 及时回复 Issues
- 接受 Pull Requests
- 定期更新版本

## 💡 提示

1. **版本号管理**: 使用 Git Tag 标记版本
   ```bash
   git tag v1.0.0
   git push origin v1.0.0
   ```

2. **Release 发布**: 在 GitHub 创建 Release
   - 添加更新日志
   - 提供下载链接

3. **CI/CD**: 考虑添加 GitHub Actions
   - 自动测试
   - 自动打包

---

祝上传顺利！🚀
