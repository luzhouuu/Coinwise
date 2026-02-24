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

## NAS Server Connection

CoinWise 部署在 Synology NAS (DS923+) 上。连接凭据存储在 `.env` 文件中。

**连接方式:**
```bash
# 推荐：用脚本从 .env 读取并连接
bash scripts/nas.sh ssh
bash scripts/nas.sh run docker ps

# 或：手动从 .env 读取凭据并连接
source .env && sshpass -p "$NAS_SSH_PASSWORD" ssh -o StrictHostKeyChecking=no -p $NAS_SSH_PORT $NAS_SSH_USER@$NAS_SSH_HOST "<command>"
```

**环境变量 (.env):**
- `NAS_SSH_HOST` - NAS 主机地址
- `NAS_SSH_PORT` - SSH 端口
- `NAS_SSH_USER` - SSH 用户名
- `NAS_SSH_PASSWORD` - SSH 密码

**常用 NAS 操作:**
- 查看 Docker 容器: `docker ps`
- 查看磁盘空间: `df -h`
- 查看日志: `docker logs <container_name>`

## NAS Deployment

部署到 NAS 的完整流程：

### 1. 打包项目
```bash
# 创建部署包（排除不需要的文件）
tar --exclude='node_modules' --exclude='.git' --exclude='__pycache__' \
    --exclude='*.pyc' --exclude='.env' --exclude='*.db' \
    --exclude='frontend/dist' --exclude='.claude' \
    -czvf /tmp/coinwise-deploy.tar.gz .
```

### 2. 上传到 NAS
```bash
# 通过 stdin 管道上传（避免 scp 权限问题）
cat /tmp/coinwise-deploy.tar.gz | bash scripts/nas.sh run "cat > /tmp/coinwise-deploy.tar.gz"
```

### 3. 在 NAS 上部署
```bash
# SSH 连接到 NAS
bash scripts/nas.sh ssh

# 以下命令在 NAS 上执行：
cd /volume1/docker/coinwise

# 备份当前版本
cp -r . ../coinwise-backup-$(date +%Y%m%d)

# 解压新版本
tar -xzvf /tmp/coinwise-deploy.tar.gz

# 重建并启动容器
docker-compose --env-file .env down
docker-compose --env-file .env build --no-cache
docker-compose --env-file .env up -d

# 查看日志确认启动成功
docker-compose logs -f --tail=50
```

### 4. 验证部署
```bash
# 检查容器状态
bash scripts/nas.sh run "cd /volume1/docker/coinwise && docker-compose ps"

# 测试 API
bash scripts/nas.sh run "curl -s http://localhost:8000/api/v1/health"
```

### 快速部署脚本
```bash
# 一键打包并上传
tar --exclude='node_modules' --exclude='.git' --exclude='__pycache__' \
    --exclude='*.pyc' --exclude='.env' --exclude='*.db' \
    --exclude='frontend/dist' --exclude='.claude' \
    -czvf /tmp/coinwise-deploy.tar.gz . && \
cat /tmp/coinwise-deploy.tar.gz | bash scripts/nas.sh run "cat > /tmp/coinwise-deploy.tar.gz"
```

### 注意事项
- NAS 上的 `.env` 文件需要单独维护，不要覆盖
- 数据库文件 `family_spending.db` 存储在容器卷中，不会被覆盖
- 登录凭据: 用户名和密码在 NAS 的 `.env` 文件中配置 (`ADMIN_USERNAME`, `ADMIN_PASSWORD`)
