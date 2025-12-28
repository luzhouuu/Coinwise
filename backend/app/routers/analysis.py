"""LLM-powered spending analysis router."""
import os
from datetime import datetime, timedelta
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy.orm import Session
from sqlalchemy import func

from ..database import get_db, TransactionModel, CategoryModel

router = APIRouter(prefix="/analysis", tags=["analysis"])


class AnalysisRequest(BaseModel):
    """Request for spending analysis."""
    year: Optional[int] = None
    month: Optional[int] = None


class AnalysisResponse(BaseModel):
    """Response containing AI analysis."""
    analysis: str
    period: str
    total_spending: float
    top_categories: list


def get_monthly_summary(db: Session, year: int, month: int) -> dict:
    """Get monthly spending summary for LLM context."""
    start_date = datetime(year, month, 1)
    if month == 12:
        end_date = datetime(year + 1, 1, 1)
    else:
        end_date = datetime(year, month + 1, 1)

    # Get transactions with categories
    results = (
        db.query(
            CategoryModel.name,
            func.count(TransactionModel.id).label("count"),
            func.sum(TransactionModel.amount).label("total"),
        )
        .join(CategoryModel, TransactionModel.category_id == CategoryModel.id, isouter=True)
        .filter(
            TransactionModel.transaction_date >= start_date,
            TransactionModel.transaction_date < end_date,
            TransactionModel.transaction_type == "withdrawal",
        )
        .group_by(CategoryModel.name)
        .order_by(func.sum(TransactionModel.amount).desc())
        .all()
    )

    # Get top transactions
    top_transactions = (
        db.query(TransactionModel)
        .filter(
            TransactionModel.transaction_date >= start_date,
            TransactionModel.transaction_date < end_date,
            TransactionModel.transaction_type == "withdrawal",
        )
        .order_by(TransactionModel.amount.desc())
        .limit(10)
        .all()
    )

    categories = []
    total = 0
    for name, count, amount in results:
        cat_name = name or "未分类"
        categories.append({
            "name": cat_name,
            "count": count,
            "amount": float(amount) if amount else 0,
        })
        total += float(amount) if amount else 0

    top_txns = [
        {"date": t.transaction_date.strftime("%m-%d"), "amount": t.amount, "desc": t.description[:30]}
        for t in top_transactions
    ]

    return {
        "year": year,
        "month": month,
        "total": total,
        "categories": categories,
        "top_transactions": top_txns,
    }


def build_prompt(summary: dict) -> str:
    """Build prompt for LLM analysis."""
    cat_text = "\n".join(
        f"- {c['name']}: ¥{c['amount']:,.0f} ({c['count']}笔)"
        for c in summary["categories"]
    )

    top_txn_text = "\n".join(
        f"- {t['date']}: ¥{t['amount']:,.0f} - {t['desc']}"
        for t in summary["top_transactions"]
    )

    return f"""请分析以下{summary['year']}年{summary['month']}月的家庭支出数据，并给出简洁的分析和建议。

## 支出概览
- 总支出: ¥{summary['total']:,.0f}

## 分类明细
{cat_text}

## 最大10笔支出
{top_txn_text}

请用中文回答，包含以下内容：
1. 本月支出概况（1-2句话）
2. 主要支出分析（哪些类别占比较大，是否合理）
3. 异常支出提醒（如有）
4. 省钱建议（1-2条具体建议）

回答要简洁，总共不超过200字。"""


async def call_gemini_api(prompt: str) -> str:
    """Call Google Gemini API for analysis."""
    import httpx

    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        return "⚠️ 未配置 GEMINI_API_KEY，请在 .env 文件中添加 API Key 后重试。"

    try:
        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.post(
                f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash:generateContent?key={api_key}",
                headers={"content-type": "application/json"},
                json={
                    "contents": [{"parts": [{"text": prompt}]}],
                    "generationConfig": {
                        "maxOutputTokens": 500,
                        "temperature": 0.7,
                    },
                },
            )

            if response.status_code == 200:
                data = response.json()
                return data["candidates"][0]["content"]["parts"][0]["text"]
            else:
                return f"⚠️ API 调用失败: {response.status_code} - {response.text}"

    except Exception as e:
        return f"⚠️ 分析请求失败: {str(e)}"


def get_latest_month_with_data(db: Session) -> tuple[int, int]:
    """Get the latest month that has transaction data."""
    result = (
        db.query(
            func.strftime('%Y', TransactionModel.transaction_date).label('year'),
            func.strftime('%m', TransactionModel.transaction_date).label('month'),
        )
        .filter(TransactionModel.transaction_type == "withdrawal")
        .order_by(TransactionModel.transaction_date.desc())
        .first()
    )

    if result and result.year and result.month:
        return int(result.year), int(result.month)

    # Fallback to current month
    now = datetime.now()
    return now.year, now.month


@router.post("/monthly", response_model=AnalysisResponse)
async def analyze_monthly_spending(
    request: AnalysisRequest,
    db: Session = Depends(get_db),
):
    """Analyze monthly spending using LLM."""
    # Default to latest month with data
    if request.year and request.month:
        year, month = request.year, request.month
    else:
        year, month = get_latest_month_with_data(db)

    # Get summary data
    summary = get_monthly_summary(db, year, month)

    if summary["total"] == 0:
        return AnalysisResponse(
            analysis="本月暂无支出记录。",
            period=f"{year}年{month}月",
            total_spending=0,
            top_categories=[],
        )

    # Build prompt and call LLM
    prompt = build_prompt(summary)
    analysis = await call_gemini_api(prompt)

    return AnalysisResponse(
        analysis=analysis,
        period=f"{year}年{month}月",
        total_spending=summary["total"],
        top_categories=summary["categories"][:5],
    )
