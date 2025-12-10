"""月度支出概览"""
import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime
import calendar

from src.firefly_client import FireflyClient

st.set_page_config(page_title="月度概览", page_icon="📅", layout="wide")
st.title("月度支出概览")


@st.cache_data(ttl=300)
def load_transactions(start_date: str, end_date: str) -> pd.DataFrame:
    client = FireflyClient()
    df = client.get_transactions(start_date=start_date, end_date=end_date, limit=500)
    if not df.empty:
        df["date"] = pd.to_datetime(df["date"])
    return df


# 月份选择
col1, col2 = st.columns(2)
with col1:
    year = st.selectbox("年份", range(2024, 2026), index=1)
with col2:
    month = st.selectbox("月份", range(1, 13), index=datetime.now().month - 1)

# 计算日期范围
first_day = datetime(year, month, 1)
last_day = datetime(year, month, calendar.monthrange(year, month)[1])

df = load_transactions(
    start_date=first_day.strftime("%Y-%m-%d"),
    end_date=last_day.strftime("%Y-%m-%d")
)

if df.empty:
    st.warning("该月份没有交易记录")
    st.stop()

df_expenses = df[df["type"] == "withdrawal"].copy()

# 月度概览
st.header(f"{year}年{month}月支出概览")

col1, col2, col3 = st.columns(3)
total = df_expenses["amount"].sum()
days_in_month = calendar.monthrange(year, month)[1]
avg_daily = total / days_in_month

with col1:
    st.metric("本月总支出", f"¥{total:,.2f}")
with col2:
    st.metric("日均支出", f"¥{avg_daily:,.2f}")
with col3:
    st.metric("交易笔数", len(df_expenses))

# 日支出热力图
st.subheader("日支出分布")

df_expenses["day"] = df_expenses["date"].dt.day
df_expenses["weekday"] = df_expenses["date"].dt.dayofweek

daily_sum = df_expenses.groupby("day")["amount"].sum().reset_index()
daily_sum.columns = ["日期", "金额"]

# 创建日历热力图数据
weeks = []
current_week = [None] * 7
first_weekday = first_day.weekday()

for day in range(1, days_in_month + 1):
    weekday = (first_weekday + day - 1) % 7
    amount = daily_sum[daily_sum["日期"] == day]["金额"].sum()
    current_week[weekday] = amount if amount > 0 else 0

    if weekday == 6 or day == days_in_month:
        weeks.append(current_week)
        current_week = [None] * 7

# 显示日支出柱状图
fig_daily = px.bar(
    daily_sum,
    x="日期",
    y="金额",
    title="每日支出",
    text_auto=".0f"
)
fig_daily.update_traces(textposition="outside")
st.plotly_chart(fig_daily, use_container_width=True)

# 按星期分布
st.subheader("按星期分布")

weekday_names = ["周一", "周二", "周三", "周四", "周五", "周六", "周日"]
weekday_expense = df_expenses.groupby("weekday")["amount"].sum().reset_index()
weekday_expense["weekday_name"] = weekday_expense["weekday"].map(lambda x: weekday_names[x])

fig_weekday = px.bar(
    weekday_expense,
    x="weekday_name",
    y="amount",
    title="按星期支出分布",
    labels={"weekday_name": "星期", "amount": "金额"}
)
st.plotly_chart(fig_weekday, use_container_width=True)

# 分类明细
st.subheader("分类明细")

category_expense = df_expenses.groupby("category")["amount"].sum().reset_index()
category_expense.columns = ["分类", "金额"]
category_expense = category_expense.sort_values("金额", ascending=False)
category_expense["占比"] = (category_expense["金额"] / category_expense["金额"].sum() * 100).round(1).astype(str) + "%"

st.dataframe(category_expense, use_container_width=True, hide_index=True)

# TOP 10 支出
st.subheader("TOP 10 支出")

top10 = df_expenses.nlargest(10, "amount")[["date", "description", "amount", "category"]]
top10.columns = ["日期", "描述", "金额", "分类"]
st.dataframe(top10, use_container_width=True, hide_index=True)
