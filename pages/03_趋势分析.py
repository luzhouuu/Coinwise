"""趋势分析"""
import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta

from src.firefly_client import FireflyClient

st.set_page_config(page_title="趋势分析", page_icon="📈", layout="wide")
st.title("支出趋势分析")


@st.cache_data(ttl=300)
def load_transactions(start_date: str, end_date: str) -> pd.DataFrame:
    client = FireflyClient()
    df = client.get_transactions(start_date=start_date, end_date=end_date, limit=2000)
    if not df.empty:
        df["date"] = pd.to_datetime(df["date"])
        df["month"] = df["date"].dt.to_period("M").astype(str)
        df["week"] = df["date"].dt.isocalendar().week
        df["year"] = df["date"].dt.year
    return df


# 加载全年数据
current_year = datetime.now().year
start_date = f"{current_year - 1}-01-01"
end_date = datetime.now().strftime("%Y-%m-%d")

df = load_transactions(start_date, end_date)

if df.empty:
    st.warning("没有交易记录")
    st.stop()

df_expenses = df[df["type"] == "withdrawal"].copy()

# 月度趋势
st.header("月度支出趋势")

monthly = df_expenses.groupby("month")["amount"].sum().reset_index()
monthly.columns = ["月份", "金额"]

# 计算环比增长
monthly["环比增长"] = monthly["金额"].pct_change() * 100

fig_monthly = go.Figure()
fig_monthly.add_trace(go.Bar(
    x=monthly["月份"],
    y=monthly["金额"],
    name="支出金额",
    text=monthly["金额"].round(0),
    textposition="outside"
))
fig_monthly.add_trace(go.Scatter(
    x=monthly["月份"],
    y=monthly["金额"],
    mode="lines+markers",
    name="趋势线",
    yaxis="y"
))
fig_monthly.update_layout(title="月度支出趋势", yaxis_title="金额 (CNY)")
st.plotly_chart(fig_monthly, use_container_width=True)

# 显示环比数据
st.subheader("月度环比变化")
monthly_display = monthly.copy()
monthly_display["环比增长"] = monthly_display["环比增长"].fillna(0).round(1).astype(str) + "%"
monthly_display["金额"] = monthly_display["金额"].apply(lambda x: f"¥{x:,.2f}")
st.dataframe(monthly_display, use_container_width=True, hide_index=True)

# 周度趋势
st.header("周度支出趋势")

weekly = df_expenses.groupby([df_expenses["date"].dt.isocalendar().year, df_expenses["date"].dt.isocalendar().week])["amount"].sum().reset_index()
weekly.columns = ["年", "周", "金额"]
weekly["周标签"] = weekly["年"].astype(str) + "-W" + weekly["周"].astype(str).str.zfill(2)

fig_weekly = px.line(
    weekly.tail(20),  # 最近20周
    x="周标签",
    y="金额",
    title="最近20周支出趋势",
    markers=True
)
st.plotly_chart(fig_weekly, use_container_width=True)

# 年度对比
st.header("年度对比")

years = sorted(df_expenses["year"].unique())
if len(years) > 1:
    yearly_comparison = df_expenses.groupby("year")["amount"].agg(["sum", "mean", "count"]).round(2)
    yearly_comparison.columns = ["总支出", "平均单笔", "交易次数"]
    yearly_comparison = yearly_comparison.reset_index()
    yearly_comparison.columns = ["年份", "总支出", "平均单笔", "交易次数"]

    col1, col2 = st.columns(2)

    with col1:
        fig_yearly = px.bar(
            yearly_comparison,
            x="年份",
            y="总支出",
            title="年度支出对比",
            text_auto=".2f"
        )
        st.plotly_chart(fig_yearly, use_container_width=True)

    with col2:
        st.dataframe(yearly_comparison, use_container_width=True, hide_index=True)

    # 同期对比
    st.subheader("同期对比")

    current_month = datetime.now().month
    ytd_comparison = df_expenses[df_expenses["date"].dt.month <= current_month].groupby("year")["amount"].sum().reset_index()
    ytd_comparison.columns = ["年份", f"1-{current_month}月累计支出"]

    st.dataframe(ytd_comparison, use_container_width=True, hide_index=True)

# 移动平均
st.header("7日移动平均")

daily = df_expenses.groupby(df_expenses["date"].dt.date)["amount"].sum().reset_index()
daily.columns = ["日期", "金额"]
daily["7日移动平均"] = daily["金额"].rolling(window=7, min_periods=1).mean()

fig_ma = go.Figure()
fig_ma.add_trace(go.Scatter(
    x=daily["日期"],
    y=daily["金额"],
    mode="lines",
    name="日支出",
    opacity=0.3
))
fig_ma.add_trace(go.Scatter(
    x=daily["日期"],
    y=daily["7日移动平均"],
    mode="lines",
    name="7日移动平均",
    line=dict(width=2)
))
fig_ma.update_layout(title="日支出与7日移动平均", yaxis_title="金额 (CNY)")
st.plotly_chart(fig_ma, use_container_width=True)
