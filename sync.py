#!/usr/bin/env python3
"""账单同步脚本 - 从邮箱获取账单并同步到 Firefly III"""
import argparse
from datetime import datetime
from dateutil.relativedelta import relativedelta

from firefly_bill_sync.config import Config
from firefly_bill_sync.email_fetcher import EmailFetcher
from firefly_bill_sync.firefly_client import FireflyClient
from firefly_bill_sync.parsers import CCBCreditCardParser, CMBCreditCardParser, ABCCreditCardParser


def get_last_month_start():
    """获取上个月第一天"""
    now = datetime.now()
    last_month = now - relativedelta(months=1)
    return datetime(last_month.year, last_month.month, 1).strftime("%d-%b-%Y")


def sync_bills(since_date: str = None, dry_run: bool = False):
    """
    同步所有账单

    Args:
        since_date: 起始日期，格式 "1-JAN-2025"
        dry_run: 如果为 True，只解析不提交
    """
    if since_date is None:
        # 默认同步上个月的账单
        since_date = get_last_month_start()

    print(f"开始同步账单，起始日期: {since_date}")

    # 初始化解析器
    parsers = [
        CCBCreditCardParser(),
        CMBCreditCardParser(),
        ABCCreditCardParser(),
    ]

    # 初始化 Firefly 客户端
    firefly = FireflyClient()

    total_synced = 0

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
                print(f"  搜索主题: {subjects}")

                emails = fetcher.fetch_emails_by_subject(
                    target_subjects=subjects,
                    since_date=since_date
                )

                for html_content, email_date in emails:
                    print(f"  解析邮件: {email_date}")
                    df = parser.parse(html_content, email_date)

                    if df.empty:
                        print("    无交易记录")
                        continue

                    print(f"    找到 {len(df)} 条交易")

                    # 分离正常交易和退款
                    refunds = df[df["amount"] < 0].copy()
                    normal = df[df["amount"] > 0].copy()

                    if not dry_run:
                        # 处理退款：删除对应的原消费记录
                        for _, row in refunds.iterrows():
                            refund_amount = abs(row["amount"])
                            print(f"    处理退款: {row['description']} | ¥{refund_amount}")
                            deleted = firefly.find_and_delete_transaction(
                                date=row["date"],
                                amount=refund_amount,
                                description=row["description"]
                            )
                            if not deleted:
                                print(f"    未找到对应的原交易")

                        # 处理正常交易（去重）
                        synced = 0
                        skipped = 0
                        for _, row in normal.iterrows():
                            # 检查是否已存在
                            if firefly.transaction_exists(row["date"], row["amount"], row["description"]):
                                skipped += 1
                                continue
                            # 创建交易
                            result = firefly.create_transaction(
                                date=row["date"],
                                amount=row["amount"],
                                description=row["description"]
                            )
                            if result:
                                synced += 1
                        total_synced += synced
                        print(f"    同步: {synced} 条, 跳过重复: {skipped} 条, 退款: {len(refunds)} 条")
                    else:
                        print(f"    [dry-run] 正常交易: {len(normal)} 条, 退款: {len(refunds)} 条")
                        if not normal.empty:
                            print(normal.head())

        finally:
            fetcher.logout()

    print(f"\n同步完成，共同步 {total_synced} 条交易")


def main():
    parser = argparse.ArgumentParser(description="同步信用卡账单到 Firefly III")
    parser.add_argument(
        "--since",
        type=str,
        help="起始日期，格式: 1-JAN-2025",
        default=None
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="只解析不提交"
    )

    args = parser.parse_args()
    sync_bills(since_date=args.since, dry_run=args.dry_run)


if __name__ == "__main__":
    main()
