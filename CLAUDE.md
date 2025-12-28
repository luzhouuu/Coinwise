# CLAUDE.md

This file provides guidance to Claude Code when working with this repository.

## Project Overview

**CoinWise** - 智能家庭支出管理系统，包含 Vue 3 前端和 FastAPI 后端。

## Common Commands

```bash
# 启动后端
cd backend && uvicorn app.main:app --reload --env-file ../.env

# 启动前端
cd frontend && npm run dev

# 同步账单
python sync_local.py --months 6

# 构建前端
cd frontend && npm run build
```

## Architecture

### Frontend (Vue 3 + TypeScript)
- `frontend/src/views/` - 页面组件
- `frontend/src/components/` - 可复用组件
- `frontend/src/api/` - API 客户端
- `frontend/src/stores/` - Pinia 状态管理

### Backend (FastAPI + SQLite)
- `backend/app/routers/` - API 路由
- `backend/app/services/` - 业务逻辑
- `backend/app/models/` - Pydantic 模型
- `backend/app/database.py` - 数据库模型

### Bill Sync Module
- `firefly_bill_sync/parsers/` - 银行账单解析器
- `firefly_bill_sync/email_fetcher.py` - IMAP 邮箱连接
- `sync_local.py` - 同步脚本入口

## Key Features
- 自动分类: `backend/app/services/categorizer.py`
- AI 分析: `backend/app/routers/analysis.py` (Gemini API)
- 预算管理: `backend/app/routers/budgets.py`

## Supported Banks
- 招商银行 (CMB): `firefly_bill_sync/parsers/cmb_parser.py`
- 建设银行 (CCB): `firefly_bill_sync/parsers/ccb_parser.py`
- 农业银行 (ABC): `firefly_bill_sync/parsers/abc_parser.py`
