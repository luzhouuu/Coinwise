"""分类支出分析"""
import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta

from src.firefly_client import FireflyClient

st.set_page_config(page_title="分类分析", page_icon="📊", layout="wide")
st.title("分类支出分析")


@st.cache_data(ttl=300)
def load_transactions(start_date: str, end_date: str) -> pd.DataFrame:
    client = FireflyClient()
    df = client.get_transactions(start_date=start_date, end_date=end_date, limit=1000)
    if not df.empty:
        df["date"] = pd.to_datetime(df["date"])
        df["month"] = df["date"].dt.to_period("M").astype(str)
    return df


# 日期范围选择
col1, col2 = st.columns(2)
default_end = datetime.now()
default_start = default_end - timedelta(days=180)

with col1:
    start_date = st.date_input("开始日期", value=default_start)
with col2:
    end_date = st.date_input("结束日期", value=default_end)

df = load_transactions(
    start_date=start_date.strftime("%Y-%m-%d"),
    end_date=end_date.strftime("%Y-%m-%d")
)

if df.empty:
    st.warning("没有交易记录")
    st.stop()

df_expenses = df[df["type"] == "withdrawal"].copy()

# 分类汇总
st.header("分类汇总")

category_summary = df_expenses.groupby("category").agg({
    "amount": ["sum", "mean", "count"]
}).round(2)
category_summary.columns = ["总金额", "平均金额", "交易次数"]
category_summary = category_summary.sort_values("总金额", ascending=False).reset_index()
category_summary["占比"] = (category_summary["总金额"] / category_summary["总金额"].sum() * 100).round(1)

col1, col2 = st.columns(2)

with col1:
    # 饼图
    fig_pie = px.pie(
        category_summary,
        values="总金额",
        names="category",
        title="支出分类占比",
        hole=0.4
    )
    st.plotly_chart(fig_pie, use_container_width=True)

with col2:
    # 汇总表
    st.dataframe(
        category_summary.rename(columns={"category": "分类"}),
        use_container_width=True,
        hide_index=True
    )

# 分类月度趋势
st.header("分类月度趋势")

category_monthly = df_expenses.groupby(["month", "category"])["amount"].sum().reset_index()

# 选择要显示的分类
all_categories = category_summary["category"].tolist()
selected_categories = st.multiselect(
    "选择分类",
    all_categories,
    default=all_categories[:5]  # 默认显示前5个
)

if selected_categories:
    filtered_data = category_monthly[category_monthly["category"].isin(selected_categories)]

    fig_trend = px.line(
        filtered_data,
        x="month",
        y="amount",
        color="category",
        title="分类月度趋势",
        markers=True,
        labels={"month": "月份", "amount": "金额", "category": "分类"}
    )
    st.plotly_chart(fig_trend, use_container_width=True)

    # 堆叠柱状图
    fig_stack = px.bar(
        filtered_data,
        x="month",
        y="amount",
        color="category",
        title="分类月度堆叠图",
        barmode="stack",
        labels={"month": "月份", "amount": "金额", "category": "分类"}
    )
    st.plotly_chart(fig_stack, use_container_width=True)

# 单一分类详情
st.header("分类详情")

selected_category = st.selectbox("选择分类查看详情", all_categories)

df_category = df_expenses[df_expenses["category"] == selected_category]

col1, col2, col3 = st.columns(3)
with col1:
    st.metric("总支出", f"¥{df_category['amount'].sum():,.2f}")
with col2:
    st.metric("平均单笔", f"¥{df_category['amount'].mean():,.2f}")
with col3:
    st.metric("交易次数", len(df_category))

# 该分类下的交易记录
st.subheader(f"{selected_category} 交易记录")
df_display = df_category[["date", "description", "amount"]].sort_values("date", ascending=False)
df_display.columns = ["日期", "描述", "金额"]
st.dataframe(df_display, use_container_width=True, hide_index=True)
