<p align="center">
  <img src="frontend/public/logo-192.png" alt="CoinWise Logo" width="80" height="80">
</p>

<h1 align="center">CoinWise</h1>

<p align="center">智能家庭支出管理系统 - 自动从邮箱获取信用卡账单，AI 分析支出，可视化预算管理。</p>

## 功能特性

- **账单同步**：自动从邮箱获取信用卡电子账单
- **智能分类**：基于关键词自动分类交易
- **AI 分析**：使用 Gemini AI 分析月度支出并给出建议
- **预算管理**：设置分类预算目标，追踪支出进度
- **数据可视化**：ECharts 图表展示支出趋势和分类占比
- **多语言支持**：中文/英文界面切换

## 支持的银行

| 银行 | 状态 |
|------|------|
| 招商银行 | ✅ |
| 建设银行 | ✅ |
| 农业银行 | ✅ |

## 技术栈

- **前端**：Vue 3 + TypeScript + Vite + ECharts + Pinia
- **后端**：FastAPI + SQLite + SQLAlchemy
- **AI**：Google Gemini API

## 项目结构

```
coinwise/
├── frontend/                 # Vue 3 前端
│   ├── src/
│   │   ├── api/             # API 客户端
│   │   ├── components/      # 组件
│   │   ├── views/           # 页面
│   │   ├── stores/          # Pinia 状态
│   │   └── i18n/            # 国际化
│   └── package.json
├── backend/                  # FastAPI 后端
│   └── app/
│       ├── routers/         # API 路由
│       ├── services/        # 业务逻辑
│       ├── models/          # 数据模型
│       └── database.py      # 数据库
├── firefly_bill_sync/        # 账单解析模块
│   ├── email_fetcher.py     # 邮箱 IMAP
│   ├── parsers/             # 银行解析器
│   └── config.py            # 配置
├── sync_local.py             # 本地同步脚本
├── .env                      # 环境变量
└── requirements.txt
```

## 快速开始

### 1. 安装依赖

```bash
# 后端
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt

# 前端
cd frontend
npm install
```

### 2. 配置环境变量

```bash
cp .env.example .env
```

编辑 `.env`：

```env
# 邮箱账户
EMAIL_IMAP_SERVER=imap.qq.com
EMAIL_USERNAME_1=your_email@qq.com
EMAIL_PASSWORD_1=your_imap_password

# AI 分析 (可选)
GEMINI_API_KEY=your_gemini_api_key
```

### 3. 启动服务

```bash
# 后端 (端口 8000)
cd backend
uvicorn app.main:app --reload --env-file ../.env

# 前端 (端口 5173)
cd frontend
npm run dev
```

### 4. 同步账单

```bash
# 同步过去 6 个月
python sync_local.py --months 6

# 测试模式（不提交）
python sync_local.py --months 1 --dry-run
```

## API 文档

启动后端后访问：http://localhost:8000/api/v1/docs

## 添加新银行支持

1. 在 `firefly_bill_sync/parsers/` 创建解析器
2. 继承 `BaseBillParser`
3. 实现 `SUBJECT_KEYWORDS` 和 `parse()` 方法
4. 在 `__init__.py` 中导出

```python
from .base_parser import BaseBillParser

class NewBankParser(BaseBillParser):
    SUBJECT_KEYWORDS = ["新银行信用卡账单"]

    def parse(self, html_content: str, email_date: str = None):
        # 解析 HTML，返回 DataFrame
        return pd.DataFrame(...)
```

## License

MIT
