#!/usr/bin/env python3
"""账单同步脚本 - 从邮箱获取账单并同步到本地数据库"""
import argparse
import requests
from datetime import datetime
from dateutil.relativedelta import relativedelta

from firefly_bill_sync.config import Config
from firefly_bill_sync.email_fetcher import EmailFetcher
from firefly_bill_sync.parsers import CCBCreditCardParser, CMBCreditCardParser, ABCCreditCardParser

LOCAL_API_URL = "http://localhost:8000/api/v1"


def get_months_ago_start(months: int = 6):
    """获取N个月前的15号（账单周期起始日）"""
    now = datetime.now()
    target = now - relativedelta(months=months)
    return datetime(target.year, target.month, 15).strftime("%d-%b-%Y")


def transaction_exists(date_str: str, amount: float, description: str) -> bool:
    """检查交易是否已存在"""
    try:
        # 搜索相同日期、金额、描述的交易
        resp = requests.get(
            f"{LOCAL_API_URL}/transactions",
            params={"limit": 100, "start_date": date_str, "end_date": date_str}
        )
        if resp.status_code == 200:
            data = resp.json()
            for t in data.get("items", []):
                if abs(t["amount"] - amount) < 0.01 and t["description"] == description:
                    return True
        return False
    except Exception as e:
        print(f"检查重复失败: {e}")
        return False


def create_transaction(date_str: str, amount: float, description: str, source: str = None) -> bool:
    """创建交易"""
    try:
        # 解析日期
        tx_date = datetime.strptime(date_str, "%Y-%m-%d")

        payload = {
            "transaction_date": tx_date.isoformat(),
            "amount": abs(amount),
            "description": description,
            "transaction_type": "withdrawal",  # 信用卡账单都是支出
            "source_account": source or "信用卡",
            "tags": ["自动导入"]
        }

        resp = requests.post(f"{LOCAL_API_URL}/transactions", json=payload)
        if resp.status_code in (200, 201):
            return True
        else:
            print(f"创建失败: {resp.status_code} - {resp.text[:100]}")
            return False
    except Exception as e:
        print(f"创建异常: {e}")
        return False


def sync_bills(months: int = 6, dry_run: bool = False):
    """
    同步账单到本地数据库

    Args:
        months: 同步过去几个月的数据
        dry_run: 如果为 True，只解析不提交
    """
    since_date = get_months_ago_start(months)
    print(f"开始同步账单，起始日期: {since_date} (过去{months}个月)")

    # 初始化解析器
    parsers = [
        CCBCreditCardParser(),
        CMBCreditCardParser(),
        ABCCreditCardParser(),
    ]

    total_synced = 0
    total_skipped = 0

    # 遍历所有邮箱账户
    for account in Config.EMAIL_ACCOUNTS:
        username = account["username"]
        password = account["password"]

        print(f"\n处理邮箱: {username}")
        fetcher = EmailFetcher(username, password)

        if not fetcher.login():
            continue

        try:
            # 对每个解析器获取对应的邮件
            for parser in parsers:
                subjects = parser.get_subject_keywords()
                bank_name = subjects[0] if subjects else "未知银行"
                print(f"\n  搜索: {bank_name}")

                emails = fetcher.fetch_emails_by_subject(
                    target_subjects=subjects,
                    since_date=since_date
                )

                for html_content, email_date in emails:
                    print(f"  解析邮件: {email_date[:20]}...")
                    df = parser.parse(html_content, email_date)

                    if df.empty:
                        continue

                    normal = df.copy()

                    if normal.empty:
                        continue

                    print(f"    找到 {len(normal)} 条交易")

                    if not dry_run:
                        synced = 0
                        skipped = 0
                        for _, row in normal.iterrows():
                            # 检查是否已存在
                            if transaction_exists(row["date"], row["amount"], row["description"]):
                                skipped += 1
                                continue
                            # 创建交易
                            if create_transaction(row["date"], row["amount"], row["description"], bank_name):
                                synced += 1

                        total_synced += synced
                        total_skipped += skipped
                        if synced > 0 or skipped > 0:
                            print(f"    同步: {synced} 条, 跳过重复: {skipped} 条")
                    else:
                        print(f"    [dry-run] 交易: {len(normal)} 条")
                        print(normal[["date", "amount", "description"]].head(3).to_string())

        finally:
            fetcher.logout()

    print(f"\n===== 同步完成 =====")
    print(f"新增: {total_synced} 条")
    print(f"跳过: {total_skipped} 条")


def main():
    parser = argparse.ArgumentParser(description="同步信用卡账单到本地数据库")
    parser.add_argument(
        "--months",
        type=int,
        default=6,
        help="同步过去几个月的数据 (默认: 6)"
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="只解析不提交"
    )

    args = parser.parse_args()
    sync_bills(months=args.months, dry_run=args.dry_run)


if __name__ == "__main__":
    main()
