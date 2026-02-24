"""农业银行信用卡账单解析器"""
import re
import pandas as pd
from bs4 import BeautifulSoup
from datetime import datetime
from typing import List

from .base_parser import BaseBillParser
from .description_cleaner import clean_description


class ABCCreditCardParser(BaseBillParser):
    """农业银行金穗信用卡账单解析器"""

    SUBJECT_KEYWORDS = ["中国农业银行金穗信用卡电子对账单"]

    def parse(self, html_content: str, email_date: str = None) -> pd.DataFrame:
        """
        解析农行信用卡 HTML 账单

        Args:
            html_content: HTML 内容
            email_date: 邮件日期

        Returns:
            DataFrame with columns: date, amount, description
        """
        soup = BeautifulSoup(html_content, "html.parser")
        tables = soup.find_all("table")

        result_data = []

        # 查找消费和退款表格
        # 消费表格：行数较多，包含 6 列，第 4 列包含 "/CNY"
        for table in tables:
            rows = table.find_all("tr")
            if len(rows) < 3:
                continue

            for row in rows:
                cells = [td.get_text(strip=True) for td in row.find_all(["td", "th"])]

                # 检查是否是有效的交易行（6列，包含日期格式 YYMMDD）
                if len(cells) != 6:
                    continue

                # 检查第一列是否是日期格式 (YYMMDD)
                if not re.match(r"^\d{6}$", cells[0]):
                    continue

                # 跳过分期记录（描述包含"分期本金"）
                if "分期本金" in cells[3]:
                    continue

                try:
                    # 解析日期 (YYMMDD -> YYYY-MM-DD)
                    date_str = cells[0]
                    year = 2000 + int(date_str[:2])
                    month = int(date_str[2:4])
                    day = int(date_str[4:6])
                    date = f"{year:04d}-{month:02d}-{day:02d}"

                    # 解析金额（从第 6 列，入账金额）
                    amount_str = cells[5]  # 如 "-199.90/CNY" 或 "248.50/CNY"
                    amount_match = re.match(r"(-?[\d,]+\.?\d*)/CNY", amount_str)
                    if not amount_match:
                        continue

                    amount = float(amount_match.group(1).replace(",", ""))
                    # 农行入账金额是反向的：消费为负，退款为正
                    # 需要取反以符合系统约定：消费为正，退款为负
                    amount = -amount

                    # 描述
                    description = clean_description(cells[3])

                    result_data.append({
                        "date": date,
                        "amount": amount,
                        "description": description
                    })

                except Exception as e:
                    print(f"处理行失败 {cells}: {e}")
                    continue

        return pd.DataFrame(result_data)
