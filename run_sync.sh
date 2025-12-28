#!/bin/bash
# Firefly Bill Sync - 自动同步脚本
# 每月15号自动执行，同步上月账单到 Firefly III

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
LOG_FILE="$SCRIPT_DIR/sync.log"
VENV_PATH="$SCRIPT_DIR/.venv"

# 记录开始时间
echo "========================================" >> "$LOG_FILE"
echo "同步开始: $(date '+%Y-%m-%d %H:%M:%S')" >> "$LOG_FILE"

# 激活虚拟环境
if [ -d "$VENV_PATH" ]; then
    source "$VENV_PATH/bin/activate"
fi

# 切换到脚本目录
cd "$SCRIPT_DIR"

# 执行同步
python sync.py >> "$LOG_FILE" 2>&1

# 记录结束时间
echo "同步结束: $(date '+%Y-%m-%d %H:%M:%S')" >> "$LOG_FILE"
echo "========================================" >> "$LOG_FILE"
echo "" >> "$LOG_FILE"
