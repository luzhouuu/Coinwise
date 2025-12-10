import pdfplumber
import pandas as pd
import re
from datetime import datetime


def parse_combined_line(line):
    # 与之前类似的正则和解析逻辑
    pattern = r'^(\d{4})\s+(\d{4})\s+(.*?)\s+([¥-]?\d+(?:\.\d{2})?)\s+(\d{4})\s+([¥-]?\d+(?:\.\d{2})?)\s+([A-Z]{2})$'
    match = re.match(pattern, line.strip())
    if not match:
        return None

    date_str, code_str, merchant, amount_str, card_last4, converted_amount_str, currency = match.groups()
    current_year = datetime.now().year
    month = int(date_str[:2])
    day = int(date_str[2:])
    date_obj = datetime(current_year, month, day)

    def parse_amount(a):
        return float(a.replace('¥', '').replace(',', '').strip())

    amount = parse_amount(amount_str)
    converted_amount = parse_amount(converted_amount_str)

    return {
        'date': date_obj.date(),
        'code': code_str,
        'merchant': merchant.strip(),
        'amount': amount,
        'card_last4': card_last4,
        'converted_amount': converted_amount,
        'currency': currency
    }


def extract_cmbc_transactions(pdf_path):
    transactions = []
    category = None
    buffer_lines = []  # 用来暂存一条完整交易记录的多行文本

    # 用于识别交易起始行的简单正则（只匹配开始部分），根据实际情况调整
    start_pattern = re.compile(r'^\d{4}\s+\d{4}\s+')

    with pdfplumber.open(pdf_path) as pdf:
        for page in pdf.pages:
            text = page.extract_text()
            if not text:
                continue

            lines = text.split('\n')
            for line in lines:
                # 首先判定分类
                if "退款" in line:
                    # 遇到新的分类，先处理前面缓冲的记录
                    if buffer_lines:
                        combined_line = " ".join(buffer_lines)
                        data = parse_combined_line(combined_line)
                        if data and category in ['退款', '消费']:
                            data['category'] = category
                            transactions.append(data)
                        buffer_lines = []
                    category = "退款"
                    continue
                elif "消费" in line:
                    # 同理，处理前面缓冲的记录
                    if buffer_lines:
                        combined_line = " ".join(buffer_lines)
                        data = parse_combined_line(combined_line)
                        if data and category in ['退款', '消费']:
                            data['category'] = category
                            transactions.append(data)
                        buffer_lines = []
                    category = "消费"
                    continue

                # 根据start_pattern判断是否是新交易开始行
                if start_pattern.match(line):
                    # 如果缓冲区中有上一条记录，则先处理上一条
                    if buffer_lines:
                        combined_line = " ".join(buffer_lines)
                        data = parse_combined_line(combined_line)
                        if data and category in ['退款', '消费']:
                            data['category'] = category
                            transactions.append(data)
                        buffer_lines = []
                    # 开始新的交易记录
                    buffer_lines.append(line.strip())
                else:
                    # 当前行不匹配起始格式，可能是上一交易记录的续行（商户名换行）
                    if buffer_lines:
                        # 将此行与前一行合并（加空格）
                        buffer_lines.append(line.strip())

    # 最后一页处理完后，缓冲区可能还有最后一条未处理的记录
    if buffer_lines:
        combined_line = " ".join(buffer_lines)
        data = parse_combined_line(combined_line)
        if data and category in ['退款', '消费']:
            data['type'] = category
            data['category'] = ''
            transactions.append(data)
    # modify date format
    df = transactions_to_dataframe(transactions)
    return df

# 转换为DataFrame并保存
def transactions_to_dataframe(transactions):
    # df = pd.DataFrame(transactions)
    # df.rename(columns={"交易日": "date",
    #                    "交易描述": "description",
    #                    "交易金额": "currency",
    #                    "结算金额": "amount"},
    #           inplace=True)
    # df = df[["date", "description", "currency", "amount"]]

    df = pd.DataFrame(transactions)
    # df['date'] = pd.to_datetime(df['date']).dt.strftime('%m/%d/%Y')
    df['currency'] = df['currency'].replace('CN', 'CNY')
    df.rename(columns={"merchant": "description"}, inplace=True)
    return df

if __name__ == "__main__":
    pdf_file = "/Users/joe.lu/Downloads/QQ邮箱 - 打印邮件.pdf"
    df = extract_cmbc_transactions(pdf_file)

    print(df)
    # df.to_csv('t.csv')
