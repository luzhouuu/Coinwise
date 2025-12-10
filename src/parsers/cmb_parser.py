"""招商银行信用卡账单解析器"""
import re
import pandas as pd
from bs4 import BeautifulSoup
from datetime import datetime
from typing import Optional

from .base_parser import BaseBillParser


class CMBCreditCardParser(BaseBillParser):
    """招商银行信用卡账单解析器"""

    SUBJECT_KEYWORDS = ["招商银行信用卡电子账单"]

    def parse(self, html_content: str, email_date: str = None) -> pd.DataFrame:
        """
        解析招行信用卡 HTML 账单

        Args:
            html_content: HTML 内容
            email_date: 邮件日期，用于处理跨年日期

        Returns:
            DataFrame with columns: date, amount, description
        """
        soup = BeautifulSoup(html_content, 'html.parser')

        # 收集所有表格行
        td_texts = []
        for tr in soup.find_all("tr")[1:]:
            cells = [td.text.strip() for td in tr.find_all("td")]
            if cells:
                td_texts.append(cells)

        # 只保留最后一列是 "CN" 的行（人民币交易）
        transcript = [row for row in td_texts if len(row) > 0 and row[-1] == "CN"]

        # 取有效列（8列结构，取第2-8列）
        transcript = [row[1:] for row in transcript if len(row) == 8]

        # 解析邮件日期
        bill_date_naive = self._parse_email_date(email_date)

        # 转换为标准格式
        result_data = []
        for row in transcript:
            try:
                # row[0] 是月日 (MMDD)
                date_temp = datetime.strptime(row[0], "%m%d").replace(year=datetime.now().year)

                # 如果日期晚于账单日期，说明是去年
                if bill_date_naive and date_temp > bill_date_naive:
                    date_temp = date_temp.replace(year=date_temp.year - 1)

                date_str = date_temp.strftime("%Y-%m-%d")

                # row[3] 是金额，如 ¥1,000
                amount_str = row[3].replace('¥', '').replace('\xa0', '').replace(',', '').strip()

                # 跳过负数
                if not amount_str or amount_str.startswith('-'):
                    continue

                amount = float(amount_str)
                description = row[2]

                result_data.append({
                    "date": date_str,
                    "amount": amount,
                    "description": description
                })
            except Exception as e:
                print(f"处理行失败 {row}: {e}")
                continue

        return pd.DataFrame(result_data)

    def _parse_email_date(self, email_date: str) -> Optional[datetime]:
        """解析邮件日期"""
        if not email_date:
            return None

        # 清理日期字符串
        date_clean = re.sub(r"\s*\(.*\)$", "", email_date)

        formats = [
            "%a, %d %b %Y %H:%M:%S %z",
            "%a, %d %b %Y %H:%M:%S",
            "%d %b %Y %H:%M:%S %z",
        ]

        for fmt in formats:
            try:
                dt = datetime.strptime(date_clean, fmt)
                return dt.replace(tzinfo=None)
            except ValueError:
                continue

        print(f"无法解析日期: {email_date}")
        return datetime.now()
