#!/usr/bin/env python3
"""添加初始黑名单规则"""

import sys
sys.path.insert(0, '/Users/joe.lu/Documents/05_ToolCode/family_spending/backend')

from app.database import SessionLocal, TransactionBlacklistModel, init_db

# 初始黑名单规则
INITIAL_BLACKLIST = [
    {
        "pattern": "深圳前海华侨城瑞吉酒店",
        "reason": "公司报销"
    },
    {
        "pattern": "深圳南山香格里拉酒店前台",
        "reason": "公司报销"
    },
    {
        "pattern": "深圳市鸿荣源西岸商业管理",
        "reason": "公司报销"
    },
]


def add_blacklist_rules():
    """添加初始黑名单规则"""
    # 初始化数据库表
    init_db()

    db = SessionLocal()
    try:
        added = 0
        for rule in INITIAL_BLACKLIST:
            # 检查是否已存在
            existing = db.query(TransactionBlacklistModel).filter(
                TransactionBlacklistModel.pattern == rule["pattern"]
            ).first()

            if existing:
                print(f"已存在: {rule['pattern']}")
                continue

            # 添加新规则
            new_rule = TransactionBlacklistModel(
                pattern=rule["pattern"],
                reason=rule.get("reason"),
            )
            db.add(new_rule)
            added += 1
            print(f"添加: {rule['pattern']}")

        db.commit()
        print(f"\n总计添加 {added} 条规则")

        # 列出所有规则
        print("\n当前黑名单:")
        all_rules = db.query(TransactionBlacklistModel).all()
        for r in all_rules:
            status = "启用" if r.is_active else "禁用"
            print(f"  [{status}] {r.pattern} - {r.reason or '无说明'}")

    finally:
        db.close()


if __name__ == "__main__":
    add_blacklist_rules()
