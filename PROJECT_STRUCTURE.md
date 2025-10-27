# 📁 项目结构说明

## 完整目录树

```
A股股票闪卡/
│
├── backend/                    # 后端目录
│   ├── __init__.py            # Python包标识文件
│   ├── app.py                 # Flask主应用（核心后端逻辑）
│   ├── config.py              # 配置文件（Token、缓存等设置）
│   └── cache/                 # 数据缓存目录（运行时自动生成）
│       ├── stock_list.json    # 股票列表缓存
│       └── stocks/            # 单个股票详细数据缓存
│           └── *.json         # 各股票缓存文件
│
├── frontend/                   # 前端目录
│   ├── index.html             # 主页面（HTML结构）
│   ├── styles.css             # 样式文件（所有CSS样式）
│   └── app.js                 # 应用逻辑（所有JavaScript代码）
│
├── run.py                      # 启动脚本（快速启动应用）
├── requirements.txt            # Python依赖列表
├── .gitignore                 # Git忽略文件配置
├── LICENSE                     # MIT开源协议
│
├── README.md                   # 项目主文档（完整说明）
├── QUICKSTART.md              # 快速启动指南（5分钟上手）
├── DEPLOYMENT.md              # 部署文档（生产环境部署）
├── PROJECT_STRUCTURE.md       # 本文件（项目结构说明）
│
└── 项目需求文档.md             # 原始需求文档（产品设计）
```

## 📄 核心文件说明

### 后端文件

#### `backend/app.py` (主应用文件)
**功能**：Flask后端API服务
- 提供RESTful API接口
- Tushare数据获取和处理
- 智能缓存管理
- 股票数据格式化

**主要接口**：
- `GET /` - 前端页面
- `GET /api/random-stock` - 获取随机股票
- `GET /api/stock/<ts_code>` - 获取指定股票
- `GET /api/stats` - 统计信息

**核心函数**：
```python
get_stock_list()         # 获取A股列表
get_stock_data()         # 获取股票数据（带缓存）
get_stock_basic_info()   # 从Tushare获取基本信息
is_cache_valid()         # 检查缓存有效性
```

#### `backend/config.py` (配置文件)
**功能**：应用配置管理
- Tushare Token配置
- 缓存策略配置
- 环境变量管理
- 开发/生产环境配置

**配置项**：
```python
TUSHARE_TOKEN        # Tushare API Token
CACHE_DIR            # 缓存目录
CACHE_TTL_HOURS      # 缓存过期时间
API_RETRY_TIMES      # API重试次数
MAX_HISTORY_YEARS    # 历史数据年限
```

### 前端文件

#### `frontend/index.html` (页面结构)
**功能**：应用HTML结构
- 顶部状态栏（已浏览、收藏数）
- 主卡片区域（双面卡片）
- 底部操作区（按钮）
- 收藏列表弹窗
- 新手引导遮罩

**主要元素**：
```html
<header>           # 顶部导航栏
<main>            # 主内容区
  <div.card>      # 卡片容器
    <div.card-front>   # 卡片正面
    <div.card-back>    # 卡片反面
<footer>          # 底部操作栏
<div.modal>       # 收藏列表弹窗
<div.guide>       # 新手引导
```

#### `frontend/styles.css` (样式文件)
**功能**：应用所有样式和动画
- 响应式布局设计
- 渐变色和多巴胺配色
- 卡片翻转动画
- 滑动动画效果
- 移动端/桌面端适配

**主要样式模块**：
```css
/* 全局样式和变量 */
:root { --primary-color: ... }

/* 布局 */
.header, .main-container, .footer

/* 卡片 */
.card, .card-front, .card-back

/* 动画 */
@keyframes swipeLeft, swipeRight, flip

/* 响应式 */
@media (max-width: 768px)
```

#### `frontend/app.js` (应用逻辑)
**功能**：前端JavaScript逻辑
- API数据获取
- 卡片交互（翻转、滑动）
- 收藏管理
- LocalStorage数据持久化
- 新手引导流程

**核心函数**：
```javascript
init()                  # 应用初始化
loadRandomStock()       # 加载随机股票
updateCardUI()          # 更新卡片UI
handleLike()            # 收藏操作
handleDislike()         # 放弃操作
handleCardClick()       # 翻转卡片
showFavorites()         # 显示收藏列表
```

**状态管理**：
```javascript
currentStock            # 当前显示股票
viewedStocks           # 已浏览股票列表
favoriteStocks         # 收藏股票列表
isFlipped              # 卡片翻转状态
isAnimating            # 动画进行中状态
```

### 配置文件

#### `requirements.txt` (Python依赖)
```
Flask==3.0.0          # Web框架
Flask-CORS==4.0.0     # 跨域支持
tushare==1.4.3        # 金融数据接口
pandas==2.1.4         # 数据处理
numpy==1.26.2         # 数值计算
requests==2.31.0      # HTTP请求
```

#### `.gitignore` (Git忽略规则)
忽略的内容：
- Python缓存文件 (`__pycache__/`)
- 虚拟环境 (`venv/`)
- 数据缓存 (`backend/cache/`)
- IDE配置 (`.vscode/`, `.idea/`)
- 环境变量 (`.env`)

### 启动文件

#### `run.py` (启动脚本)
**功能**：一键启动应用
- 自动配置Python路径
- 读取环境变量
- 显示启动信息
- 启动Flask服务

**使用**：
```bash
python run.py
```

### 文档文件

#### `README.md` (主文档)
**内容**：
- 项目介绍和特性
- 完整安装指南
- 使用说明
- API文档
- 技术栈说明
- 未来规划

#### `QUICKSTART.md` (快速指南)
**内容**：
- 5分钟快速启动
- 简化的安装步骤
- 基本使用方法
- 常见问题解答

#### `DEPLOYMENT.md` (部署文档)
**内容**：
- 生产环境部署详细步骤
- 服务器配置（Nginx、Gunicorn）
- SSL证书配置
- 监控和维护
- 故障排除

#### `PROJECT_STRUCTURE.md` (本文档)
**内容**：
- 完整项目结构
- 每个文件的作用
- 代码组织说明

## 🔄 数据流程

### 1. 启动流程
```
run.py
  ↓
backend/app.py (初始化Flask)
  ↓
创建缓存目录
  ↓
配置Tushare
  ↓
启动HTTP服务
  ↓
提供前端页面 (frontend/)
```

### 2. 用户访问流程
```
用户访问 http://localhost:5000
  ↓
Flask返回 frontend/index.html
  ↓
浏览器加载 styles.css 和 app.js
  ↓
app.js 初始化
  ↓
调用 /api/random-stock
  ↓
显示第一张卡片
```

### 3. 数据获取流程
```
前端请求股票数据
  ↓
后端检查缓存
  ↓
[缓存有效] ──→ 返回缓存数据 ⚡
  ↓
[缓存无效]
  ↓
调用Tushare API
  ↓
处理和格式化数据
  ↓
保存到缓存
  ↓
返回数据
```

### 4. 用户交互流程
```
用户操作（滑动/点击）
  ↓
触发事件处理器
  ↓
更新UI动画
  ↓
保存到LocalStorage
  ↓
加载下一张卡片
```

## 📦 缓存结构

### `backend/cache/stock_list.json`
```json
{
  "cache_time": "2024-01-15T09:00:00",
  "stocks": [
    {
      "ts_code": "000001.SZ",
      "symbol": "000001",
      "name": "平安银行",
      "industry": "银行",
      ...
    }
  ]
}
```

### `backend/cache/stocks/000001.SZ.json`
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
  "from_cache": false
}
```

## 🗄️ LocalStorage结构

### `viewedStocks`
```json
["000001.SZ", "600000.SH", "000002.SZ", ...]
```

### `favoriteStocks`
```json
[
  {
    "ts_code": "000001.SZ",
    "name": "平安银行",
    "code": "000001",
    "time": "2024-01-15T10:30:00"
  }
]
```

### `hasSeenGuide`
```json
"true"
```

## 🎨 设计模式

### 后端：MVC变体
- **Model**：Tushare API + 缓存系统
- **View**：JSON API响应
- **Controller**：Flask路由处理器

### 前端：模块化JavaScript
- **状态管理**：全局变量
- **UI更新**：函数式更新
- **事件处理**：事件监听器
- **数据持久化**：LocalStorage

## 🔧 扩展点

### 后端扩展
- `backend/models.py` - 数据模型
- `backend/services.py` - 业务逻辑
- `backend/utils.py` - 工具函数
- `backend/cache_manager.py` - 缓存管理器

### 前端扩展
- `frontend/components/` - 组件化
- `frontend/utils.js` - 工具函数
- `frontend/api.js` - API封装
- `frontend/store.js` - 状态管理

## 📝 开发建议

### 修改样式
编辑 `frontend/styles.css`，修改CSS变量：
```css
:root {
  --primary-color: #667eea;  /* 主色调 */
  --secondary-color: #764ba2; /* 次色调 */
}
```

### 修改逻辑
编辑 `frontend/app.js`，主要函数：
- 加载数据：`loadRandomStock()`
- UI更新：`updateCardUI()`
- 用户交互：`handle*()`

### 修改后端
编辑 `backend/app.py`，主要部分：
- API路由：`@app.route()`
- 数据获取：`get_stock_*()`
- 缓存逻辑：`is_cache_valid()`

---

**理解项目结构后，就可以轻松进行二次开发了！** 🚀

