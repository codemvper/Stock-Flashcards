# 🚀 部署文档

本文档详细说明如何将A股上市公司闪卡应用部署到生产环境。

## 📋 部署前准备

### 1. 服务器要求
- **操作系统**：Ubuntu 20.04+ / CentOS 7+
- **内存**：至少 1GB RAM
- **存储**：至少 10GB 可用空间
- **Python**：3.8 或更高版本
- **网络**：需要访问 Tushare API

### 2. 域名和备案
- 准备已备案的域名
- 配置DNS解析指向服务器IP
- 申请SSL证书（推荐使用Let's Encrypt免费证书）

### 3. Tushare Token
- 注册 Tushare Pro 账号：https://tushare.pro/register
- 获取 API Token
- 建议升级至积分套餐以获得更高的API调用限额

---

## 🛠️ 部署步骤

### 步骤 1：连接服务器

```bash
ssh root@your-server-ip
```

### 步骤 2：安装系统依赖

#### Ubuntu/Debian
```bash
sudo apt update
sudo apt upgrade -y
sudo apt install -y python3 python3-pip python3-venv nginx git
```

#### CentOS/RHEL
```bash
sudo yum update -y
sudo yum install -y python3 python3-pip nginx git
```

### 步骤 3：创建应用用户

```bash
sudo useradd -m -s /bin/bash stockapp
sudo usermod -aG sudo stockapp
```

### 步骤 4：下载项目代码

```bash
# 切换到应用用户
su - stockapp

# 克隆项目
git clone <your-repository-url> ~/stock-flashcard
cd ~/stock-flashcard
```

### 步骤 5：配置Python虚拟环境

```bash
# 创建虚拟环境
python3 -m venv venv

# 激活虚拟环境
source venv/bin/activate

# 安装依赖
pip install --upgrade pip
pip install -r requirements.txt
pip install gunicorn
```

### 步骤 6：配置环境变量

```bash
# 复制环境变量模板
cp .env.example .env

# 编辑环境变量
nano .env
```

在 `.env` 文件中配置：
```
SECRET_KEY=生成一个随机密钥
DEBUG=False
HOST=127.0.0.1
PORT=5000
TUSHARE_TOKEN=你的Tushare Token
CACHE_TTL_HOURS=24
```

生成随机密钥：
```bash
python3 -c "import secrets; print(secrets.token_hex(32))"
```

### 步骤 7：测试应用

```bash
# 激活虚拟环境
source venv/bin/activate

# 启动应用
python run.py
```

访问 `http://服务器IP:5000` 测试应用是否正常运行。

测试成功后按 `Ctrl+C` 停止应用。

### 步骤 8：配置Gunicorn

创建 Gunicorn 配置文件：

```bash
nano gunicorn_config.py
```

添加以下内容：
```python
# Gunicorn配置
import multiprocessing

# 监听地址
bind = "127.0.0.1:5000"

# 工作进程数
workers = multiprocessing.cpu_count() * 2 + 1

# 工作模式
worker_class = "sync"

# 超时时间
timeout = 120

# 日志
accesslog = "/home/stockapp/stock-flashcard/logs/access.log"
errorlog = "/home/stockapp/stock-flashcard/logs/error.log"
loglevel = "info"

# 进程名称
proc_name = "stock-flashcard"

# Daemon
daemon = False
```

创建日志目录：
```bash
mkdir -p ~/stock-flashcard/logs
```

### 步骤 9：配置Systemd服务

```bash
sudo nano /etc/systemd/system/stock-flashcard.service
```

添加以下内容：
```ini
[Unit]
Description=A股上市公司闪卡应用
After=network.target

[Service]
Type=notify
User=stockapp
Group=stockapp
WorkingDirectory=/home/stockapp/stock-flashcard
Environment="PATH=/home/stockapp/stock-flashcard/venv/bin"
EnvironmentFile=/home/stockapp/stock-flashcard/.env
ExecStart=/home/stockapp/stock-flashcard/venv/bin/gunicorn \
    --config gunicorn_config.py \
    backend.app:app

Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
```

启动并启用服务：
```bash
sudo systemctl daemon-reload
sudo systemctl start stock-flashcard
sudo systemctl enable stock-flashcard
```

检查服务状态：
```bash
sudo systemctl status stock-flashcard
```

### 步骤 10：配置Nginx

创建Nginx配置文件：
```bash
sudo nano /etc/nginx/sites-available/stock-flashcard
```

添加以下内容：
```nginx
server {
    listen 80;
    server_name your-domain.com www.your-domain.com;

    # 日志
    access_log /var/log/nginx/stock-flashcard-access.log;
    error_log /var/log/nginx/stock-flashcard-error.log;

    # 客户端最大上传大小
    client_max_body_size 10M;

    # 代理到Gunicorn
    location / {
        proxy_pass http://127.0.0.1:5000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        
        # 超时设置
        proxy_connect_timeout 60s;
        proxy_send_timeout 60s;
        proxy_read_timeout 60s;
    }

    # 静态文件缓存
    location ~* \.(jpg|jpeg|png|gif|ico|css|js)$ {
        proxy_pass http://127.0.0.1:5000;
        expires 7d;
        add_header Cache-Control "public, immutable";
    }
}
```

启用站点：
```bash
sudo ln -s /etc/nginx/sites-available/stock-flashcard /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl restart nginx
```

### 步骤 11：配置SSL证书（可选但推荐）

使用 Let's Encrypt 免费证书：

```bash
# 安装Certbot
sudo apt install -y certbot python3-certbot-nginx

# 获取证书并自动配置Nginx
sudo certbot --nginx -d your-domain.com -d www.your-domain.com

# 设置自动续期
sudo certbot renew --dry-run
```

### 步骤 12：配置防火墙

```bash
# UFW防火墙（Ubuntu）
sudo ufw allow 22/tcp    # SSH
sudo ufw allow 80/tcp    # HTTP
sudo ufw allow 443/tcp   # HTTPS
sudo ufw enable

# Firewalld（CentOS）
sudo firewall-cmd --permanent --add-service=ssh
sudo firewall-cmd --permanent --add-service=http
sudo firewall-cmd --permanent --add-service=https
sudo firewall-cmd --reload
```

---

## 🔍 验证部署

访问您的域名：`https://your-domain.com`

检查以下功能：
- [ ] 页面能正常加载
- [ ] 能随机获取股票数据
- [ ] 卡片翻转动画正常
- [ ] 左右滑动操作正常
- [ ] 收藏功能正常
- [ ] 响应式布局正常

---

## 📊 监控和维护

### 查看应用日志

```bash
# Systemd日志
sudo journalctl -u stock-flashcard -f

# Gunicorn日志
tail -f ~/stock-flashcard/logs/error.log
tail -f ~/stock-flashcard/logs/access.log

# Nginx日志
sudo tail -f /var/log/nginx/stock-flashcard-error.log
sudo tail -f /var/log/nginx/stock-flashcard-access.log
```

### 重启服务

```bash
# 重启应用
sudo systemctl restart stock-flashcard

# 重启Nginx
sudo systemctl restart nginx

# 重新加载Nginx配置（无需停止服务）
sudo nginx -s reload
```

### 更新代码

```bash
cd ~/stock-flashcard
git pull
source venv/bin/activate
pip install -r requirements.txt
sudo systemctl restart stock-flashcard
```

### 清理缓存

```bash
cd ~/stock-flashcard
rm -rf backend/cache/*
```

### 备份数据

```bash
# 备份缓存数据
tar -czf backup_$(date +%Y%m%d).tar.gz backend/cache/

# 备份到远程服务器
scp backup_*.tar.gz user@backup-server:/backup/stock-flashcard/
```

---

## 🔧 故障排除

### 应用无法启动

1. 检查服务状态
```bash
sudo systemctl status stock-flashcard
```

2. 查看错误日志
```bash
sudo journalctl -u stock-flashcard -n 50
```

3. 检查Python依赖
```bash
source venv/bin/activate
pip list
```

### 502 Bad Gateway

1. 确认Gunicorn运行正常
```bash
sudo systemctl status stock-flashcard
```

2. 检查端口是否被监听
```bash
sudo netstat -tulpn | grep 5000
```

3. 检查Nginx配置
```bash
sudo nginx -t
```

### API调用失败

1. 检查Tushare Token是否正确
2. 检查服务器网络连接
3. 查看API调用日志
```bash
tail -f ~/stock-flashcard/logs/error.log
```

### 性能问题

1. 增加Gunicorn工作进程数
2. 启用Nginx缓存
3. 使用Redis替代文件缓存
4. 升级服务器配置

---

## 📈 性能优化

### 1. 启用Gzip压缩

在Nginx配置中添加：
```nginx
gzip on;
gzip_types text/plain text/css application/json application/javascript text/xml application/xml;
gzip_min_length 1000;
```

### 2. 配置Redis缓存（可选）

安装Redis：
```bash
sudo apt install redis-server
```

修改应用配置使用Redis替代文件缓存。

### 3. CDN加速（可选）

将静态资源上传到CDN，加快全国访问速度。

### 4. 数据库优化（未来）

如需存储用户数据，可配置PostgreSQL或MySQL数据库。

---

## 🔐 安全建议

1. **定期更新系统**
```bash
sudo apt update && sudo apt upgrade -y
```

2. **配置SSH密钥登录**，禁用密码登录

3. **使用fail2ban防止暴力破解**
```bash
sudo apt install fail2ban
```

4. **定期备份数据**

5. **监控服务器资源使用情况**

6. **设置定期更新SSL证书**

---

## 📞 技术支持

如遇到部署问题，请：
1. 查看日志文件
2. 检查系统资源（内存、磁盘）
3. 提交Issue到项目仓库
4. 联系技术支持

---

**部署成功后，记得及时更新DNS记录，并测试所有功能！** 🎉

