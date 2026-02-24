"""建设银行信用卡账单解析器"""
import re
import pandas as pd
from bs4 import BeautifulSoup
from typing import Optional

from .base_parser import BaseBillParser
from .description_cleaner import clean_description


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

        # 查找交易明细表格
        # 策略：找到包含6列表头行 ['交易日', '银行记账日', ...] 且有8列数据行的表格
        tables = soup.find_all("table")
        target_table = None
        header_keywords = ['交易日', '银行记账日', '卡号后四位', '交易描述']

        best_table = None
        best_count = 0

        for table in tables:
            rows = table.find_all("tr", recursive=False)  # 只找直接子行，避免嵌套
            if not rows:
                rows = table.find_all("tr")

            has_header = False
            data_count = 0

            for tr in rows:
                cells = tr.find_all(["td", "th"])
                cell_texts = [c.get_text(strip=True) for c in cells]

                # 检查是否是表头行（6列且包含关键词）
                if len(cells) == 6 and all(kw in ' '.join(cell_texts) for kw in header_keywords):
                    has_header = True
                # 检查是否是数据行（8列）
                elif len(cells) == 8:
                    data_count += 1

            if has_header and data_count > best_count:
                best_count = data_count
                best_table = table

        target_table = best_table

        if not target_table:
            print("未找到交易明细表格")
            return pd.DataFrame(columns=["date", "amount", "description"])

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
            # 查找表头行（精确匹配原始格式）
            header_patterns = [
                ['交易日', '银行记账日', '卡号后四位', '交易描述', '交易币/金额', '结算币/金额'],
            ]

            idx_start = None
            idx_end = None

            for i, row in enumerate(rows):
                # 检查是否是表头行
                for header in header_patterns:
                    if all(h in row for h in header):
                        idx_start = i
                        break
                # 检查结束标记
                row_text = ' '.join(row)
                if '结束' in row_text or 'The End' in row_text:
                    idx_end = i
                    break

            if idx_start is None:
                # 回退：查找包含"交易日"的行
                for i, row in enumerate(rows):
                    if '交易日' in row:
                        idx_start = i
                        break

            if idx_start is None:
                print("未找到表头行")
                return pd.DataFrame(columns=["date", "amount", "description"])

            if idx_end is None:
                idx_end = len(rows)

            # 筛选有效数据行（8列）
            data_rows = [row for row in rows[idx_start:idx_end] if len(row) == 8]

            if not data_rows:
                # 尝试其他列数
                for col_count in [6, 7, 9]:
                    data_rows = [row for row in rows[idx_start:idx_end] if len(row) == col_count]
                    if data_rows:
                        print(f"使用 {col_count} 列格式")
                        break

            if not data_rows:
                print(f"未找到有效数据行，行数: {len(rows[idx_start:idx_end])}")
                if rows[idx_start:idx_end]:
                    print(f"示例行列数: {[len(r) for r in rows[idx_start:idx_start+5]]}")
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
                description = clean_description(row[3])  # 交易描述
                amount_str = row[7]  # 结算币/金额

                # 清理金额
                amount_str = amount_str.replace(',', '').replace('¥', '').replace('\xa0', '').strip()

                # 跳过无效金额
                if not amount_str:
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
