# 📱 A股上市公司闪卡

<div align="center">

一个现代化的WEB应用，通过闪卡形式帮助投资者快速了解A股上市公司的基本面情况。支持移动端和桌面端，提供左右滑动操作、收藏管理、财务指标对比等功能。

![Python](https://img.shields.io/badge/Python-3.8+-blue.svg)
![Flask](https://img.shields.io/badge/Flask-3.0.0-green.svg)
![License](https://img.shields.io/badge/License-MIT-yellow.svg)
![GitHub stars](https://img.shields.io/github/stars/yourusername/a-share-flashcards?style=social)
![GitHub forks](https://img.shields.io/github/forks/yourusername/a-share-flashcards?style=social)

[快速开始](#-快速开始) | [功能特性](#-核心功能) | [API文档](#-api接口)

</div>



## ✨ 核心功能

### 📊 闪卡浏览
- **随机刷卡**：智能随机展示公司，避免重复
- **左右滑动**：左滑放弃，右滑收藏
- **双面卡片**：正面基本信息，反面财务指标
- **进度跟踪**：实时显示已浏览公司数量

### 💰 财务分析
- **核心指标**：ROE、PE、PB三大财务指标
- **可视化展示**：进度条直观显示指标水平
- **数据对比**：历史纵向对比和同行业横向对比

### ⭐ 收藏管理
- **一键收藏**：右滑或点击按钮收藏公司
- **收藏列表**：统一管理收藏的公司
- **快速访问**：收藏列表可快速查看和取消收藏

### 🎨 用户体验
- **响应式设计**：完美适配手机、平板、桌面
- **流畅动画**：丝滑的翻转和滑动效果
- **新手引导**：首次使用自动显示操作指引
- **本地存储**：浏览记录和收藏本地保存

## 🚀 快速开始

### 📋 环境要求

- **Python**: 3.8+ (推荐 3.11+)
- **操作系统**: Windows / macOS / Linux
- **浏览器**: Chrome 80+ / Firefox 75+ / Safari 13+ / Edge 80+

### ⚡ 一键安装

```bash
# 1. 克隆项目
git clone https://github.com/codemvper/a-share-flashcards.git
cd a-share-flashcards

# 2. 创建虚拟环境（推荐）
python -m venv venv

# 3. 激活虚拟环境
# Windows
venv\Scripts\activate
# macOS/Linux
source venv/bin/activate

# 4. 安装依赖
pip install -r requirements.txt

# 5. 配置Tushare Token
export TUSHARE_TOKEN="your_tushare_token_here"

# 6. 启动应用
python run.py
```

### 🔑 获取Tushare Token

1. 访问 [Tushare官网](https://tushare.pro/register) 注册账号
2. 登录后在个人中心获取Token
3. 配置Token的三种方式：

**方式一：环境变量（推荐）**
```bash
# Windows
set TUSHARE_TOKEN=your_token_here

# macOS/Linux
export TUSHARE_TOKEN=your_token_here
```

**方式二：配置文件**
编辑 `backend/config.py`：
```python
TUSHARE_TOKEN = "your_token_here"
```

**方式三：运行时输入**
首次运行时程序会提示输入Token

### 🌐 访问应用

启动成功后，打开浏览器访问：
- **本地访问**: http://localhost:5000
- **局域网访问**: http://your-ip:5000

### 🔧 故障排除

<details>
<summary>常见问题解决方案</summary>

**问题1: pip安装失败**
```bash
# 升级pip
python -m pip install --upgrade pip

# 使用国内镜像源
pip install -r requirements.txt -i https://pypi.tuna.tsinghua.edu.cn/simple/
```

**问题2: Tushare API调用失败**
- 检查Token是否正确配置
- 确认网络连接正常
- 免费账号有调用频率限制，请适当降低使用频率

**问题3: 端口被占用**
```bash
# 查看端口占用
netstat -ano | findstr :5000

# 修改端口（在run.py中）
app.run(host='0.0.0.0', port=8080, debug=True)
```

**问题4: 缓存数据异常**
```bash
# 清理缓存
rm -rf cache/
# 或手动删除cache文件夹
```

</details>

## 📁 项目结构

```
a-share-flashcards/
├── 📂 backend/                    # 🔧 后端服务
│   ├── 📄 app.py                 # Flask应用主文件
│   ├── 📄 config.py              # 配置文件
│   └── 📄 __init__.py            # 包初始化文件
├── 📂 frontend/                   # 🎨 前端界面
│   ├── 📄 index.html             # 主页面
│   ├── 📄 styles.css             # 样式文件
│   └── 📄 app.js                 # 应用逻辑
├── 📂 cache/                      # 💾 数据缓存（运行时生成）
│   ├── 📄 README.md              # 缓存说明文档
│   ├── 📄 stock_list.json        # 股票列表缓存
│   ├── 📂 stocks/                # 股票详细数据缓存
│   └── 📂 historical/            # 历史数据缓存
├── 📄 requirements.txt           # 📦 Python依赖包
├── 📄 run.py                     # 🚀 应用启动脚本
├── 📄 .gitignore                 # 🚫 Git忽略规则
├── 📄 README.md                  # 📖 项目说明文档
├── 📄 LICENSE                    # ⚖️ 开源协议
├── 📄 DEPLOYMENT.md              # 🚀 部署指南
├── 📄 PROJECT_STRUCTURE.md       # 📋 项目结构说明
└── 📄 QUICKSTART.md              # ⚡ 快速开始指南
```

### 📂 核心目录说明

| 目录/文件 | 说明 | 重要性 |
|-----------|------|--------|
| `backend/` | Flask后端服务，处理API请求和数据获取 | ⭐⭐⭐ |
| `frontend/` | 前端界面，纯HTML/CSS/JS实现 | ⭐⭐⭐ |
| `cache/` | 数据缓存目录，提升响应速度 | ⭐⭐ |
| `requirements.txt` | Python依赖包列表 | ⭐⭐⭐ |
| `run.py` | 应用启动入口 | ⭐⭐⭐ |

## 🔧 技术栈

<div align="center">

| 分类 | 技术 | 版本 | 说明 |
|------|------|------|------|
| **🔧 后端框架** | Flask | 3.0.0 | 轻量级Web框架 |
| **🌐 跨域处理** | Flask-CORS | 4.0.0 | 跨域资源共享 |
| **📊 数据源** | Tushare | 1.4.3 | 金融数据API |
| **📈 数据处理** | Pandas | 2.1.4 | 数据分析库 |
| **🔢 数值计算** | NumPy | 1.26.2 | 科学计算库 |
| **🌍 HTTP请求** | Requests | 2.31.0 | HTTP库 |

</div>

### 🎨 前端技术

- **🏗️ 核心技术**: 原生HTML5 + CSS3 + JavaScript (ES6+)
- **📱 响应式设计**: CSS Flexbox + Grid + Media Queries
- **💾 数据存储**: LocalStorage API
- **🎭 动画效果**: CSS Animations + Transitions
- **👆 触摸支持**: Touch Events + Pointer Events
- **⌨️ 键盘支持**: Keyboard Events

### 🏗️ 架构特点

- **🔄 前后端分离**: RESTful API设计
- **💾 智能缓存**: 24小时TTL本地缓存
- **📱 移动优先**: 响应式设计，完美适配各种设备
- **⚡ 高性能**: 数据预加载 + 本地缓存
- **🔒 数据安全**: 本地存储，无用户数据上传

## 📊 API接口

### 获取随机股票
```http
GET /api/random-stock?viewed=<已浏览股票代码列表>
```

**响应示例：**
```json
{
  "code": "000001",
  "name": "平安银行",
  "price": 12.34,
  "pct_chg": 1.23,
  "market_value": 2345.67,
  "industry": "银行",
  "financial": {
    "roe": 12.5,
    "pe": 8.9,
    "pb": 0.75
  },
  "cached_time": "2024-01-15T09:30:00",
  "from_cache": true
}
```

### 获取指定股票
```http
GET /api/stock/<ts_code>
```

### 获取统计信息
```http
GET /api/stats
```

## 🎯 功能特性

### 智能缓存机制
- ✅ 24小时本地缓存，减少API调用
- ✅ 股票数据按需加载，首次访问从API获取
- ✅ 后续访问直接读取缓存，响应速度快
- ✅ 自动过期检测和数据更新

### 数据获取流程
```
用户刷到股票 A
    ↓
检查本地缓存
    ↓
有缓存且未过期 → 返回缓存数据 ⚡
无缓存或已过期 → 调用Tushare API → 存储缓存 → 返回数据
```

### 响应式设计
- 📱 **手机竖屏**：卡片全屏显示，最佳浏览体验
- 📱 **手机横屏**：卡片居中，两侧留白
- 💻 **桌面端**：固定3:4宽高比，优雅居中展示
- ⌨️ **键盘支持**：左右箭头键切换，空格键翻转

### 交互操作
- 👆 **点击翻转**：查看卡片正反面
- 👈👉 **滑动操作**：左滑放弃，右滑收藏（移动端）
- 🖱️ **按钮操作**：点击底部按钮进行操作（桌面端）
- ⌨️ **键盘快捷键**：
  - `←` 放弃当前股票
  - `→` 收藏当前股票
  - `Space` 翻转卡片

## 📝 使用指南

### 首次使用

1. 打开应用后，会自动显示第一张卡片
2. 点击卡片翻转查看财务数据（引导提示）
3. 左滑或点击"放弃"按钮跳过当前公司
4. 右滑或点击"收藏"按钮收藏感兴趣的公司

### 浏览股票

- **翻转查看**：点击卡片可以翻转查看正反面信息
- **快速筛选**：根据财务指标快速判断公司质量
- **收藏管理**：随时查看和管理收藏的公司

### 数据说明

#### 正面信息
- **公司名称**：上市公司全称
- **股票代码**：6位数字代码
- **当前价格**：最新交易日收盘价
- **涨跌幅**：相对前一交易日的涨跌百分比
- **市值**：总市值（单位：亿元）
- **行业**：所属行业分类

#### 反面信息
- **ROE（净资产收益率）**：衡量公司盈利能力
- **PE（市盈率）**：股价相对盈利的倍数
- **PB（市净率）**：股价相对净资产的倍数

## 🔐 数据安全

- ✅ 所有浏览记录和收藏仅保存在本地浏览器
- ✅ 不会上传任何个人数据到服务器
- ✅ 清除浏览器数据会同时清除应用数据

## ⚠️ 注意事项

1. **Tushare限制**：免费账号每分钟调用次数有限，建议合理使用
2. **数据延迟**：股票数据可能有延迟，仅供参考，不构成投资建议
3. **缓存时间**：默认24小时缓存，可在配置文件中调整
4. **浏览器兼容**：建议使用现代浏览器（Chrome、Firefox、Safari、Edge）

## 🚀 部署指南

### 🐳 Docker部署（推荐）

<details>
<summary>点击展开Docker部署步骤</summary>

**1. 创建Dockerfile**
```dockerfile
FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

EXPOSE 5000

ENV TUSHARE_TOKEN=""

CMD ["python", "run.py"]
```

**2. 构建和运行**
```bash
# 构建镜像
docker build -t a-share-flashcards .

# 运行容器
docker run -d \
  --name stock-flashcards \
  -p 5000:5000 \
  -e TUSHARE_TOKEN="your_token_here" \
  a-share-flashcards
```

**3. 使用Docker Compose**
```yaml
version: '3.8'
services:
  app:
    build: .
    ports:
      - "5000:5000"
    environment:
      - TUSHARE_TOKEN=your_token_here
    volumes:
      - ./cache:/app/cache
    restart: unless-stopped
```

</details>

### ☁️ 云服务器部署

<details>
<summary>点击展开云服务器部署步骤</summary>

**1. 安装系统依赖**
```bash
# Ubuntu/Debian
sudo apt update
sudo apt install python3 python3-pip python3-venv nginx

# CentOS/RHEL
sudo yum update
sudo yum install python3 python3-pip nginx
```

**2. 部署应用**
```bash
# 克隆项目
git clone https://github.com/yourusername/a-share-flashcards.git
cd a-share-flashcards

# 创建虚拟环境
python3 -m venv venv
source venv/bin/activate

# 安装依赖
pip install -r requirements.txt
pip install gunicorn

# 配置环境变量
echo "export TUSHARE_TOKEN='your_token_here'" >> ~/.bashrc
source ~/.bashrc
```

**3. 使用Gunicorn部署**
```bash
# 测试运行
gunicorn -w 4 -b 0.0.0.0:5000 backend.app:app

# 后台运行
nohup gunicorn -w 4 -b 127.0.0.1:5000 backend.app:app > gunicorn.log 2>&1 &
```

**4. 配置Nginx反向代理**
```nginx
server {
    listen 80;
    server_name your-domain.com;
    
    location / {
        proxy_pass http://127.0.0.1:5000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
    
    # 静态文件缓存
    location /frontend/ {
        alias /path/to/project/frontend/;
        expires 1d;
        add_header Cache-Control "public, immutable";
    }
}
```

**5. 配置HTTPS（可选）**
```bash
# 安装Certbot
sudo apt install certbot python3-certbot-nginx

# 获取SSL证书
sudo certbot --nginx -d your-domain.com
```

**6. 使用Systemd管理服务**
```ini
# /etc/systemd/system/stock-flashcards.service
[Unit]
Description=A股股票闪卡应用
After=network.target

[Service]
Type=exec
User=www-data
Group=www-data
WorkingDirectory=/path/to/project
Environment="TUSHARE_TOKEN=your_token_here"
ExecStart=/path/to/project/venv/bin/gunicorn -w 4 -b 127.0.0.1:5000 backend.app:app
ExecReload=/bin/kill -s HUP $MAINPID
Restart=always
RestartSec=3

[Install]
WantedBy=multi-user.target
```

```bash
# 启动服务
sudo systemctl daemon-reload
sudo systemctl start stock-flashcards
sudo systemctl enable stock-flashcards

# 查看状态
sudo systemctl status stock-flashcards
```

</details>

### 🌐 Vercel部署（免费）

<details>
<summary>点击展开Vercel部署步骤</summary>

**1. 安装Vercel CLI**
```bash
npm i -g vercel
```

**2. 创建vercel.json**
```json
{
  "version": 2,
  "builds": [
    {
      "src": "run.py",
      "use": "@vercel/python"
    }
  ],
  "routes": [
    {
      "src": "/(.*)",
      "dest": "run.py"
    }
  ],
  "env": {
    "TUSHARE_TOKEN": "@tushare_token"
  }
}
```

**3. 部署**
```bash
# 登录Vercel
vercel login

# 设置环境变量
vercel env add TUSHARE_TOKEN

# 部署
vercel --prod
```

</details>

### 📊 性能优化建议

- **🔄 负载均衡**: 使用多个Gunicorn worker
- **💾 Redis缓存**: 替换文件缓存提升性能
- **📈 监控**: 使用Prometheus + Grafana监控
- **🔒 安全**: 配置防火墙和SSL证书
- **📦 CDN**: 使用CDN加速静态资源

## 📈 未来规划

### V1.1 版本
- [ ] 历史数据5年对比
- [ ] 同行业公司横向对比
- [ ] 股东人数和持股数据
- [ ] 公司主营业务介绍

### V1.2 版本
- [ ] 用户登录和云端同步
- [ ] 数据分析和统计图表
- [ ] 自定义筛选条件
- [ ] 导出收藏列表

### V1.3 版本
- [ ] 广告集成（腾讯广点通）
- [ ] 用户行为分析
- [ ] 热门股票预缓存
- [ ] PWA支持（离线使用）

## 🤝 贡献指南

我们欢迎所有形式的贡献！无论是报告bug、提出新功能建议，还是提交代码改进。

### 📝 如何贡献

1. **🍴 Fork 项目**
   ```bash
   git clone https://github.com/yourusername/a-share-flashcards.git
   ```

2. **🌿 创建特性分支**
   ```bash
   git checkout -b feature/amazing-feature
   ```

3. **💻 提交更改**
   ```bash
   git commit -m 'Add some amazing feature'
   ```

4. **📤 推送分支**
   ```bash
   git push origin feature/amazing-feature
   ```

5. **🔄 创建 Pull Request**

### 🐛 报告问题

在提交Issue前，请确保：
- [ ] 搜索现有Issue，避免重复
- [ ] 提供详细的问题描述
- [ ] 包含复现步骤
- [ ] 提供环境信息（操作系统、Python版本等）

### 💡 功能建议

我们欢迎新功能建议！请在Issue中详细描述：
- 功能的使用场景
- 预期的行为
- 可能的实现方案

### 👥 贡献者

感谢所有为这个项目做出贡献的开发者！

<a href="https://github.com/yourusername/a-share-flashcards/graphs/contributors">
  <img src="https://contrib.rocks/image?repo=yourusername/a-share-flashcards" />
</a>

## ⭐ Star History

[![Star History Chart](https://api.star-history.com/svg?repos=yourusername/a-share-flashcards&type=Date)](https://star-history.com/#yourusername/a-share-flashcards&Date)

## 📊 项目统计

![GitHub repo size](https://img.shields.io/github/repo-size/yourusername/a-share-flashcards)
![GitHub code size in bytes](https://img.shields.io/github/languages/code-size/yourusername/a-share-flashcards)
![GitHub last commit](https://img.shields.io/github/last-commit/yourusername/a-share-flashcards)
![GitHub commit activity](https://img.shields.io/github/commit-activity/m/yourusername/a-share-flashcards)

## 📄 开源协议

本项目采用 [MIT License](LICENSE) 开源协议。

## 📮 联系方式

<div align="center">

| 联系方式 | 链接 |
|---------|------|
| 📧 **Email** | [your-email@example.com](mailto:your-email@example.com) |
| 🐛 **Issues** | [GitHub Issues](https://github.com/yourusername/a-share-flashcards/issues) |
| 💬 **Discussions** | [GitHub Discussions](https://github.com/yourusername/a-share-flashcards/discussions) |
| 🐦 **Twitter** | [@yourusername](https://twitter.com/yourusername) |

</div>

## 🙏 致谢

- 感谢 [Tushare](https://tushare.pro/) 提供优质的金融数据API
- 感谢 [Flask](https://flask.palletsprojects.com/) 团队提供优秀的Web框架
- 感谢所有开源贡献者的无私奉献

## ⚖️ 免责声明

> ⚠️ **重要提醒**
> 
> 本应用提供的股票信息和财务数据仅供学习和参考，不构成任何投资建议。
> 
> - 📊 数据可能存在延迟或错误
> - 💰 投资有风险，入市需谨慎
> - 🚫 不承担任何投资损失责任
> - 📚 仅用于教育和研究目的

## 📈 支持项目

如果这个项目对您有帮助，请考虑：

- ⭐ 给项目点个Star
- 🍴 Fork并贡献代码
- 📢 分享给更多人


---

<div align="center">

**Made with ❤️ for A股投资者**

*让投资决策更智能，让财富增长更稳健*

</div>

