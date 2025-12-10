"""家庭支出可视化仪表板 - 主页"""
import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta

from src.firefly_client import FireflyClient

# 页面配置
st.set_page_config(
    page_title="家庭支出管理",
    page_icon="💰",
    layout="wide"
)

st.title("家庭支出管理仪表板")


@st.cache_data(ttl=300)
def load_transactions(start_date: str, end_date: str) -> pd.DataFrame:
    """加载交易数据（缓存5分钟）"""
    client = FireflyClient()
    df = client.get_transactions(start_date=start_date, end_date=end_date, limit=500)
    if not df.empty:
        df["date"] = pd.to_datetime(df["date"])
        df["month"] = df["date"].dt.to_period("M").astype(str)
    return df


# 侧边栏 - 日期选择
st.sidebar.header("筛选条件")

# 默认显示最近3个月
default_end = datetime.now()
default_start = default_end - timedelta(days=90)

col1, col2 = st.sidebar.columns(2)
with col1:
    start_date = st.date_input("开始日期", value=default_start)
with col2:
    end_date = st.date_input("结束日期", value=default_end)

# 加载数据
df = load_transactions(
    start_date=start_date.strftime("%Y-%m-%d"),
    end_date=end_date.strftime("%Y-%m-%d")
)

if df.empty:
    st.warning("没有找到交易记录，请检查日期范围或 API 配置")
    st.stop()

# 只显示支出
df_expenses = df[df["type"] == "withdrawal"].copy()

# 分类筛选
all_categories = ["全部"] + sorted(df_expenses["category"].dropna().unique().tolist())
selected_category = st.sidebar.selectbox("分类", all_categories)

if selected_category != "全部":
    df_expenses = df_expenses[df_expenses["category"] == selected_category]

# ===== 核心指标 =====
st.header("概览")

col1, col2, col3, col4 = st.columns(4)

total_expense = df_expenses["amount"].sum()
avg_daily = total_expense / max((end_date - start_date).days, 1)
transaction_count = len(df_expenses)
avg_per_transaction = total_expense / max(transaction_count, 1)

with col1:
    st.metric("总支出", f"¥{total_expense:,.2f}")
with col2:
    st.metric("日均支出", f"¥{avg_daily:,.2f}")
with col3:
    st.metric("交易笔数", f"{transaction_count}")
with col4:
    st.metric("笔均金额", f"¥{avg_per_transaction:,.2f}")

# ===== 图表展示 =====
st.header("支出分析")

tab1, tab2, tab3 = st.tabs(["趋势分析", "分类占比", "详细记录"])

with tab1:
    # 月度趋势
    monthly_expense = df_expenses.groupby("month")["amount"].sum().reset_index()
    monthly_expense.columns = ["月份", "金额"]

    fig_trend = px.bar(
        monthly_expense,
        x="月份",
        y="金额",
        title="月度支出趋势",
        text_auto=".2f"
    )
    fig_trend.update_traces(textposition="outside")
    st.plotly_chart(fig_trend, use_container_width=True)

    # 日支出趋势
    daily_expense = df_expenses.groupby(df_expenses["date"].dt.date)["amount"].sum().reset_index()
    daily_expense.columns = ["日期", "金额"]

    fig_daily = px.line(
        daily_expense,
        x="日期",
        y="金额",
        title="日支出趋势"
    )
    st.plotly_chart(fig_daily, use_container_width=True)

with tab2:
    col1, col2 = st.columns(2)

    with col1:
        # 分类饼图
        category_expense = df_expenses.groupby("category")["amount"].sum().reset_index()
        category_expense.columns = ["分类", "金额"]
        category_expense = category_expense.sort_values("金额", ascending=False)

        fig_pie = px.pie(
            category_expense,
            values="金额",
            names="分类",
            title="支出分类占比",
            hole=0.4
        )
        st.plotly_chart(fig_pie, use_container_width=True)

    with col2:
        # 分类柱状图
        fig_bar = px.bar(
            category_expense,
            x="分类",
            y="金额",
            title="各分类支出金额",
            text_auto=".2f"
        )
        fig_bar.update_traces(textposition="outside")
        st.plotly_chart(fig_bar, use_container_width=True)

    # 分类月度趋势
    category_monthly = df_expenses.groupby(["month", "category"])["amount"].sum().reset_index()
    category_monthly.columns = ["月份", "分类", "金额"]

    fig_category_trend = px.bar(
        category_monthly,
        x="月份",
        y="金额",
        color="分类",
        title="各分类月度支出趋势",
        barmode="stack"
    )
    st.plotly_chart(fig_category_trend, use_container_width=True)

with tab3:
    # 详细记录表
    st.subheader("交易明细")

    # 搜索过滤
    search_term = st.text_input("搜索描述")
    if search_term:
        df_display = df_expenses[df_expenses["description"].str.contains(search_term, case=False, na=False)]
    else:
        df_display = df_expenses

    # 排序
    sort_col = st.selectbox("排序字段", ["date", "amount", "category"])
    sort_order = st.radio("排序方式", ["降序", "升序"], horizontal=True)
    ascending = sort_order == "升序"

    df_display = df_display.sort_values(sort_col, ascending=ascending)

    # 显示表格
    st.dataframe(
        df_display[["date", "amount", "description", "category"]].rename(columns={
            "date": "日期",
            "amount": "金额",
            "description": "描述",
            "category": "分类"
        }),
        use_container_width=True,
        hide_index=True
    )

# 页脚
st.markdown("---")
st.caption("数据来源: Firefly III | 最后更新: " + datetime.now().strftime("%Y-%m-%d %H:%M"))
