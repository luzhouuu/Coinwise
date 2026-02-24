#!/usr/bin/env python3
"""一次性迁移脚本：清洗已有交易描述中的支付中介前缀，并删除重复记录。

用法:
    python scripts/migrate_clean_descriptions.py --dry-run   # 预览变更
    python scripts/migrate_clean_descriptions.py             # 执行迁移
"""
import argparse
import hashlib
import sqlite3
import sys
from collections import defaultdict
from pathlib import Path

# 确保项目根目录在 sys.path 中
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from firefly_bill_sync.parsers.description_cleaner import clean_description


def generate_email_id(date_str: str, description: str, amount: float) -> str:
    """与 sync_service._generate_email_id 保持一致的 hash 生成逻辑。"""
    normalized_date = str(date_str)[:10]
    normalized_desc = description.strip()
    normalized_amount = f"{amount:.2f}"
    content = f"{normalized_date}|{normalized_desc}|{normalized_amount}"
    return hashlib.md5(content.encode()).hexdigest()


def main():
    parser = argparse.ArgumentParser(
        description="清洗已有交易描述中的支付中介前缀，并删除重复记录"
    )
    parser.add_argument(
        "--dry-run", action="store_true", help="预览模式，不实际修改数据库"
    )
    parser.add_argument(
        "--db", default=None, help="数据库路径（默认: backend/family_spending.db）"
    )
    args = parser.parse_args()

    # 确定数据库路径
    if args.db:
        db_path = Path(args.db)
    else:
        db_path = project_root / "backend" / "family_spending.db"

    if not db_path.exists():
        print(f"错误: 数据库文件不存在: {db_path}")
        sys.exit(1)

    conn = sqlite3.connect(str(db_path))
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()

    # 读取所有交易
    cursor.execute(
        "SELECT id, transaction_date, amount, description, source_email_id "
        "FROM transactions ORDER BY id"
    )
    rows = cursor.fetchall()
    print(f"共 {len(rows)} 条交易记录\n")

    # ── Phase 1: 清洗描述 ──────────────────────────────────────────────
    clean_updates = []  # (id, new_desc, new_email_id)

    for row in rows:
        old_desc = row["description"] or ""
        new_desc = clean_description(old_desc)
        if new_desc != old_desc:
            new_email_id = generate_email_id(
                str(row["transaction_date"]), new_desc, row["amount"]
            )
            clean_updates.append((row["id"], new_desc, new_email_id))

    print(f"[清洗] 需要清洗描述: {len(clean_updates)} 条")
    if clean_updates:
        # 打印前 20 条示例
        for tid, new_desc, _ in clean_updates[:20]:
            orig = next(r for r in rows if r["id"] == tid)
            print(f"  [{tid}] {orig['description']!r} -> {new_desc!r}")
        if len(clean_updates) > 20:
            print(f"  ... 还有 {len(clean_updates) - 20} 条")

    # ── Phase 2: 去重（基于清洗后的 date+desc+amount）────────────────
    # 用清洗后的值构建分组
    groups = defaultdict(list)  # (date, cleaned_desc, amount) -> [row ids]
    for row in rows:
        old_desc = row["description"] or ""
        cleaned = clean_description(old_desc)
        date = str(row["transaction_date"])[:10]
        amt = f"{abs(row['amount']):.2f}"
        groups[(date, cleaned, amt)].append(row["id"])

    # 每组保留 ID 最小的记录，其余删除
    ids_to_delete = set()
    dup_groups = 0
    for key, ids in groups.items():
        if len(ids) > 1:
            dup_groups += 1
            ids_to_delete.update(sorted(ids)[1:])  # 保留最小 ID

    print(f"\n[去重] 重复组数: {dup_groups}")
    print(f"[去重] 将删除多余记录: {len(ids_to_delete)} 条")

    if ids_to_delete:
        # 打印前 10 组示例
        shown = 0
        for key, ids in sorted(groups.items()):
            if len(ids) <= 1:
                continue
            date, desc, amt = key
            keep_id = sorted(ids)[0]
            del_ids = sorted(ids)[1:]
            print(f"  {date} | {amt} | {desc}")
            print(f"    保留 ID={keep_id}, 删除 IDs={del_ids}")
            shown += 1
            if shown >= 10:
                print(f"  ... 还有 {dup_groups - 10} 组")
                break

    # ── 汇总 ──────────────────────────────────────────────────────────
    # 只清洗不删除的记录数（被删除的不需要更新）
    clean_only = [(tid, desc, eid) for tid, desc, eid in clean_updates if tid not in ids_to_delete]

    print(f"\n{'=' * 50}")
    print(f"  清洗描述: {len(clean_only)} 条")
    print(f"  删除重复: {len(ids_to_delete)} 条")
    final_count = len(rows) - len(ids_to_delete)
    print(f"  最终记录: {final_count} 条 (原 {len(rows)} 条)")
    print(f"{'=' * 50}")

    if args.dry_run:
        print("\n(预览模式，未修改数据库)")
        conn.close()
        return

    # ── 执行 ──────────────────────────────────────────────────────────
    # 备份提醒
    backup_path = str(db_path) + ".backup"
    print(f"\n正在备份数据库到 {backup_path} ...")
    import shutil
    shutil.copy2(str(db_path), backup_path)
    print("备份完成。")

    # 1) 清洗描述（只更新不会被删除的记录）
    for tid, new_desc, new_email_id in clean_only:
        cursor.execute(
            "UPDATE transactions SET description = ?, source_email_id = ? WHERE id = ?",
            (new_desc, new_email_id, tid),
        )
    print(f"已清洗 {len(clean_only)} 条描述。")

    # 2) 删除重复记录
    if ids_to_delete:
        # SQLite 限制一次 IN 的参数数量，分批处理
        batch_size = 500
        del_list = sorted(ids_to_delete)
        for i in range(0, len(del_list), batch_size):
            batch = del_list[i : i + batch_size]
            placeholders = ",".join("?" * len(batch))
            cursor.execute(
                f"DELETE FROM transactions WHERE id IN ({placeholders})", batch
            )
        print(f"已删除 {len(ids_to_delete)} 条重复记录。")

    # 3) 对保留的记录也重算 source_email_id（确保 hash 基于清洗后的描述）
    # 上面 clean_only 已经处理了需要清洗的，这里处理那些描述没变但需要确认 email_id 一致的
    cursor.execute(
        "SELECT id, transaction_date, amount, description FROM transactions"
    )
    remaining = cursor.fetchall()
    recalc_count = 0
    for r in remaining:
        expected_eid = generate_email_id(
            str(r["transaction_date"]), r["description"], r["amount"]
        )
        cursor.execute(
            "UPDATE transactions SET source_email_id = ? WHERE id = ? AND (source_email_id IS NULL OR source_email_id != ?)",
            (expected_eid, r["id"], expected_eid),
        )
        recalc_count += cursor.rowcount

    if recalc_count:
        print(f"已修正 {recalc_count} 条记录的 source_email_id。")

    conn.commit()
    print(f"\n迁移完成。最终记录数: {len(remaining)} 条。")
    conn.close()


if __name__ == "__main__":
    main()
