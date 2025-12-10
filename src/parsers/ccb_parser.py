"""建设银行信用卡账单解析器"""
import re
import pandas as pd
from bs4 import BeautifulSoup
from typing import Optional

from .base_parser import BaseBillParser


class CCBCreditCardParser(BaseBillParser):
    """建设银行信用卡账单解析器"""

    SUBJECT_KEYWORDS = ["中国建设银行信用卡电子账单"]

    def parse(self, html_content: str, email_date: str = None) -> pd.DataFrame:
        """
        解析建行信用卡 HTML 账单

        Args:
            html_content: HTML 内容
            email_date: 邮件日期

        Returns:
            DataFrame with columns: date, amount, description
        """
        soup = BeautifulSoup(html_content, "html.parser")

        # 查找包含"交易日"的表格
        candidate_tables = []
        tables = soup.find_all("table")
        for table in tables:
            if table.find(string=re.compile("交易日")):
                candidate_tables.append(table)

        if not candidate_tables:
            print("未找到交易明细表格")
            return pd.DataFrame(columns=["date", "amount", "description"])

        # 选取行数最多的表格
        target_table = max(candidate_tables, key=lambda t: len(t.find_all("tr")))

        # 提取所有行
        rows = []
        for tr in target_table.find_all("tr"):
            cells = tr.find_all(["td", "th"])
            if not cells:
                continue
            row = [cell.get_text(strip=True) for cell in cells]
            rows.append(row)

        if not rows:
            return pd.DataFrame(columns=["date", "amount", "description"])

        # 找到表头和结束标记
        try:
            header_row = ['交易日', '银行记账日', '卡号后四位', '交易描述', '交易币/金额', '结算币/金额']
            idx_start = None
            idx_end = None

            for i, row in enumerate(rows):
                if '交易日' in row and '交易描述' in row:
                    idx_start = i
                if '*** 结束 The End ***' in row or 'The End' in ' '.join(row):
                    idx_end = i
                    break

            if idx_start is None:
                idx_start = 0
            if idx_end is None:
                idx_end = len(rows)

            # 筛选有效数据行（8列）
            data_rows = [row for row in rows[idx_start:idx_end] if len(row) == 8]

            if not data_rows:
                return pd.DataFrame(columns=["date", "amount", "description"])

            # 跳过表头行
            if data_rows[0][0] == '交易日':
                data_rows = data_rows[1:]

        except Exception as e:
            print(f"解析表格结构失败: {e}")
            return pd.DataFrame(columns=["date", "amount", "description"])

        # 转换为标准格式
        result_data = []
        for row in data_rows:
            try:
                date = row[0]  # 交易日
                description = row[3]  # 交易描述
                amount_str = row[7]  # 结算币/金额

                # 清理金额
                amount_str = amount_str.replace(',', '').replace('¥', '').replace('\xa0', '').strip()

                # 跳过负数（退款）或无效金额
                if not amount_str or amount_str.startswith('-'):
                    continue

                amount = float(amount_str)
                result_data.append({
                    "date": date,
                    "amount": amount,
                    "description": description
                })
            except Exception as e:
                print(f"处理行失败 {row}: {e}")
                continue

        return pd.DataFrame(result_data)
