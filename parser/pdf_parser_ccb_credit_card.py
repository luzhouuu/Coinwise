import pdfplumber
import pandas as pd
import pdfplumber
import pandas as pd

# 定义函数从PDF中提取交易明细
def extract_ccb_transaction(pdf_path):
    transactions = []
    with pdfplumber.open(pdf_path) as pdf:
        for page in pdf.pages:
            print(page)
            text = page.extract_text()
            # if "交易⽇ 银⾏记账⽇ 卡号后四位" in text:
            lines = text.split("\n")
            for line in lines:
                if any(char.isdigit() for char in line) and "CNY" in line:
                    parts = line.split()
                    if len(parts) >= 6:
                        t_date = parts[0]  # 交易日
                        p_date = parts[1]  # 记账日
                        card_number = parts[2]  # 卡号后四位
                        description = " ".join(parts[3:-2])  # 交易描述
                        amount = parts[-2]  # 交易金额
                        settlement = parts[-1]  # 结算金额
                        transactions.append(
                            {
                                "交易日": t_date,
                                "记账日": p_date,
                                "卡号后四位": card_number,
                                "交易描述": description,
                                "交易金额": amount,
                                "结算金额": settlement,
                            }
                        )

    df = transactions_to_dataframe(transactions)
    return df

# 转换为DataFrame并保存
def transactions_to_dataframe(transactions):
    df = pd.DataFrame(transactions)
    df.rename(columns={"交易日": "date",
                       "交易描述": "description",
                       "交易金额": "currency",
                       "结算金额": "amount"},
              inplace=True)
    df["amount"] = df["amount"].str.replace(",", "").astype(float)
    df = df[["date", "description", "currency", "amount"]]

    # 删除退款项目
    refund_amount = df.loc[df["amount"] < 0, 'amount'].tolist()
    refund_amount = [-i for i in refund_amount]
    refund_idx = [df[df["amount"] == i].index for i in refund_amount]
    for idx in refund_idx:
        df.drop(idx, inplace=True)
    df = df.loc[df["amount"] > 0]
    df.reset_index(drop=True, inplace=True)

    return df

# 主程序
if __name__ == "__main__":
    pdf_path = "/Users/joe.lu/Downloads/QQ邮箱 - 打印邮件.pdf"  # 替换为你的PDF路径
    df = extract_ccb_transaction(pdf_path)
    print(df)
    print(len(df))
    # 保存为Excel文件
    df.to_excel("交易明细.xlsx", index=False)
