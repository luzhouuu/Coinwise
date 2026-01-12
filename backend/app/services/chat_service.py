"""Chat service with Gemini Function Calling for precise bill queries."""
import os
import json
from datetime import datetime, timedelta
from typing import List, Optional, Any

import httpx
from sqlalchemy.orm import Session
from sqlalchemy import func, and_, or_

from ..database import TransactionModel, CategoryModel


# Define functions that Gemini can call
FUNCTION_DECLARATIONS = [
    {
        "name": "query_transactions",
        "description": "查询交易记录，支持按分类、日期、金额范围等条件过滤。用于回答关于具体交易的问题。",
        "parameters": {
            "type": "object",
            "properties": {
                "category": {
                    "type": "string",
                    "description": "分类名称，如：餐饮、交通、购物、娱乐、医疗、住房、通讯、其他"
                },
                "start_date": {
                    "type": "string",
                    "description": "开始日期，格式 YYYY-MM-DD"
                },
                "end_date": {
                    "type": "string",
                    "description": "结束日期，格式 YYYY-MM-DD"
                },
                "min_amount": {
                    "type": "number",
                    "description": "最小金额"
                },
                "max_amount": {
                    "type": "number",
                    "description": "最大金额"
                },
                "limit": {
                    "type": "integer",
                    "description": "返回条数，默认10"
                },
                "order_by": {
                    "type": "string",
                    "enum": ["amount", "date"],
                    "description": "排序字段"
                },
                "order": {
                    "type": "string",
                    "enum": ["asc", "desc"],
                    "description": "排序方向"
                },
                "search": {
                    "type": "string",
                    "description": "搜索关键词，匹配交易描述"
                }
            }
        }
    },
    {
        "name": "get_category_summary",
        "description": "获取某个分类的统计汇总，包括总金额、笔数、平均金额等。用于回答关于某分类总体情况的问题。",
        "parameters": {
            "type": "object",
            "properties": {
                "category": {
                    "type": "string",
                    "description": "分类名称"
                },
                "start_date": {
                    "type": "string",
                    "description": "开始日期，格式 YYYY-MM-DD"
                },
                "end_date": {
                    "type": "string",
                    "description": "结束日期，格式 YYYY-MM-DD"
                }
            },
            "required": ["category"]
        }
    },
    {
        "name": "get_spending_summary",
        "description": "获取指定时间段的支出汇总，包括总支出、各分类占比等。用于回答关于总体支出的问题。",
        "parameters": {
            "type": "object",
            "properties": {
                "start_date": {
                    "type": "string",
                    "description": "开始日期，格式 YYYY-MM-DD"
                },
                "end_date": {
                    "type": "string",
                    "description": "结束日期，格式 YYYY-MM-DD"
                }
            }
        }
    },
    {
        "name": "get_all_categories",
        "description": "获取所有可用的消费分类列表",
        "parameters": {
            "type": "object",
            "properties": {}
        }
    }
]


class ChatService:
    """Service for handling chat with Function Calling."""

    def __init__(self, db: Session):
        self.db = db

    def _get_category_id(self, category_name: str) -> Optional[int]:
        """Get category ID by name."""
        category = self.db.query(CategoryModel).filter(
            CategoryModel.name == category_name
        ).first()
        return category.id if category else None

    def _get_category_name(self, category_id: Optional[int]) -> str:
        """Get category name by ID."""
        if not category_id:
            return "未分类"
        category = self.db.query(CategoryModel).filter(
            CategoryModel.id == category_id
        ).first()
        return category.name if category else "未分类"

    def _get_default_date_range(self) -> tuple[datetime, datetime]:
        """Get default date range (last 6 months)."""
        end_date = datetime.now()
        start_date = end_date - timedelta(days=180)
        return start_date, end_date

    def _parse_date(self, date_str: Optional[str]) -> Optional[datetime]:
        """Parse date string to datetime."""
        if not date_str:
            return None
        try:
            return datetime.strptime(date_str, "%Y-%m-%d")
        except ValueError:
            return None

    # ========== Function Implementations ==========

    def query_transactions(
        self,
        category: Optional[str] = None,
        start_date: Optional[str] = None,
        end_date: Optional[str] = None,
        min_amount: Optional[float] = None,
        max_amount: Optional[float] = None,
        limit: int = 10,
        order_by: str = "date",
        order: str = "desc",
        search: Optional[str] = None,
    ) -> dict:
        """Query transactions with filters."""
        query = self.db.query(TransactionModel).filter(
            TransactionModel.transaction_type == "withdrawal"
        )

        # Category filter
        if category:
            cat_id = self._get_category_id(category)
            if cat_id:
                query = query.filter(TransactionModel.category_id == cat_id)

        # Date range
        start = self._parse_date(start_date)
        end = self._parse_date(end_date)
        if not start or not end:
            start, end = self._get_default_date_range()
        query = query.filter(
            TransactionModel.transaction_date >= start,
            TransactionModel.transaction_date <= end
        )

        # Amount range
        if min_amount is not None:
            query = query.filter(TransactionModel.amount >= min_amount)
        if max_amount is not None:
            query = query.filter(TransactionModel.amount <= max_amount)

        # Search
        if search:
            query = query.filter(TransactionModel.description.contains(search))

        # Ordering
        if order_by == "amount":
            order_col = TransactionModel.amount
        else:
            order_col = TransactionModel.transaction_date

        if order == "asc":
            query = query.order_by(order_col.asc())
        else:
            query = query.order_by(order_col.desc())

        # Limit
        transactions = query.limit(min(limit, 50)).all()

        # Get total count
        count_query = self.db.query(func.count(TransactionModel.id)).filter(
            TransactionModel.transaction_type == "withdrawal"
        )
        if category:
            cat_id = self._get_category_id(category)
            if cat_id:
                count_query = count_query.filter(TransactionModel.category_id == cat_id)
        count_query = count_query.filter(
            TransactionModel.transaction_date >= start,
            TransactionModel.transaction_date <= end
        )
        total_count = count_query.scalar() or 0

        return {
            "transactions": [
                {
                    "date": t.transaction_date.strftime("%Y-%m-%d"),
                    "amount": float(t.amount),
                    "description": t.description,
                    "category": self._get_category_name(t.category_id)
                }
                for t in transactions
            ],
            "total_count": total_count,
            "returned_count": len(transactions),
            "period": f"{start.strftime('%Y-%m-%d')} 至 {end.strftime('%Y-%m-%d')}"
        }

    def get_category_summary(
        self,
        category: str,
        start_date: Optional[str] = None,
        end_date: Optional[str] = None,
    ) -> dict:
        """Get summary for a specific category."""
        cat_id = self._get_category_id(category)
        if not cat_id:
            return {
                "error": f"未找到分类: {category}",
                "available_categories": [c.name for c in self.db.query(CategoryModel).all()]
            }

        start = self._parse_date(start_date)
        end = self._parse_date(end_date)
        if not start or not end:
            start, end = self._get_default_date_range()

        result = self.db.query(
            func.count(TransactionModel.id).label("count"),
            func.sum(TransactionModel.amount).label("total"),
            func.avg(TransactionModel.amount).label("avg"),
            func.max(TransactionModel.amount).label("max"),
            func.min(TransactionModel.amount).label("min"),
        ).filter(
            TransactionModel.category_id == cat_id,
            TransactionModel.transaction_type == "withdrawal",
            TransactionModel.transaction_date >= start,
            TransactionModel.transaction_date <= end,
        ).first()

        # Get largest transaction
        largest = self.db.query(TransactionModel).filter(
            TransactionModel.category_id == cat_id,
            TransactionModel.transaction_type == "withdrawal",
            TransactionModel.transaction_date >= start,
            TransactionModel.transaction_date <= end,
        ).order_by(TransactionModel.amount.desc()).first()

        return {
            "category": category,
            "period": f"{start.strftime('%Y-%m-%d')} 至 {end.strftime('%Y-%m-%d')}",
            "count": result.count or 0,
            "total_amount": float(result.total) if result.total else 0,
            "average_amount": float(result.avg) if result.avg else 0,
            "max_amount": float(result.max) if result.max else 0,
            "min_amount": float(result.min) if result.min else 0,
            "largest_transaction": {
                "date": largest.transaction_date.strftime("%Y-%m-%d"),
                "amount": float(largest.amount),
                "description": largest.description
            } if largest else None
        }

    def get_spending_summary(
        self,
        start_date: Optional[str] = None,
        end_date: Optional[str] = None,
    ) -> dict:
        """Get overall spending summary."""
        start = self._parse_date(start_date)
        end = self._parse_date(end_date)
        if not start or not end:
            start, end = self._get_default_date_range()

        # Total stats
        total_result = self.db.query(
            func.count(TransactionModel.id).label("count"),
            func.sum(TransactionModel.amount).label("total"),
        ).filter(
            TransactionModel.transaction_type == "withdrawal",
            TransactionModel.transaction_date >= start,
            TransactionModel.transaction_date <= end,
        ).first()

        # By category
        category_results = self.db.query(
            CategoryModel.name,
            func.count(TransactionModel.id).label("count"),
            func.sum(TransactionModel.amount).label("total"),
        ).join(
            CategoryModel, TransactionModel.category_id == CategoryModel.id, isouter=True
        ).filter(
            TransactionModel.transaction_type == "withdrawal",
            TransactionModel.transaction_date >= start,
            TransactionModel.transaction_date <= end,
        ).group_by(CategoryModel.name).order_by(func.sum(TransactionModel.amount).desc()).all()

        total = float(total_result.total) if total_result.total else 0
        categories = []
        for name, count, cat_total in category_results:
            cat_name = name or "未分类"
            cat_amount = float(cat_total) if cat_total else 0
            categories.append({
                "name": cat_name,
                "count": count,
                "amount": cat_amount,
                "percentage": round(cat_amount / total * 100, 1) if total > 0 else 0
            })

        return {
            "period": f"{start.strftime('%Y-%m-%d')} 至 {end.strftime('%Y-%m-%d')}",
            "total_amount": total,
            "transaction_count": total_result.count or 0,
            "categories": categories
        }

    def get_all_categories(self) -> dict:
        """Get all available categories."""
        categories = self.db.query(CategoryModel).all()
        return {
            "categories": [c.name for c in categories]
        }

    # ========== Function Executor ==========

    def execute_function(self, name: str, args: dict) -> dict:
        """Execute a function by name with given arguments."""
        if name == "query_transactions":
            return self.query_transactions(**args)
        elif name == "get_category_summary":
            return self.get_category_summary(**args)
        elif name == "get_spending_summary":
            return self.get_spending_summary(**args)
        elif name == "get_all_categories":
            return self.get_all_categories()
        else:
            return {"error": f"Unknown function: {name}"}

    # ========== Chat with Function Calling ==========

    async def chat(self, user_message: str, history: list = None) -> str:
        """Process user message with Function Calling."""
        api_key = os.getenv("GEMINI_API_KEY")
        if not api_key:
            return "抱歉，AI 服务未配置。请在设置中添加 GEMINI_API_KEY。"

        system_prompt = """你是 CoinWise 智能财务助手，帮助用户查询和分析账单数据。

使用规则：
1. 根据用户问题调用合适的函数获取数据
2. 用中文回答，简洁友好
3. 金额显示为 ¥X,XXX.XX 格式
4. 如果数据不存在，如实说明
5. 回答控制在 200 字以内

今天是 """ + datetime.now().strftime("%Y年%m月%d日") + """，如果用户说"上个月"、"这个月"等，请计算对应的日期范围。"""

        try:
            async with httpx.AsyncClient(timeout=60.0) as client:
                # Build conversation history
                contents = []
                if history:
                    for msg in history:
                        role = "user" if msg.get("role") == "user" else "model"
                        contents.append({"role": role, "parts": [{"text": msg.get("content", "")}]})
                # Add current user message
                contents.append({"role": "user", "parts": [{"text": user_message}]})

                # First call: Let Gemini decide which function to call
                response = await client.post(
                    f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash:generateContent?key={api_key}",
                    headers={"content-type": "application/json"},
                    json={
                        "contents": contents,
                        "systemInstruction": {"parts": [{"text": system_prompt}]},
                        "tools": [{"functionDeclarations": FUNCTION_DECLARATIONS}],
                        "generationConfig": {
                            "temperature": 0.1,
                        },
                    },
                )

                if response.status_code != 200:
                    return f"抱歉，AI 服务暂时不可用。错误: {response.status_code}"

                data = response.json()
                candidate = data.get("candidates", [{}])[0]
                content = candidate.get("content", {})
                parts = content.get("parts", [])

                # Check if Gemini wants to call a function
                function_call = None
                for part in parts:
                    if "functionCall" in part:
                        function_call = part["functionCall"]
                        break

                if function_call:
                    # Execute the function
                    func_name = function_call["name"]
                    func_args = function_call.get("args", {})
                    func_result = self.execute_function(func_name, func_args)

                    # Second call: Let Gemini generate response based on function result
                    response2 = await client.post(
                        f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash:generateContent?key={api_key}",
                        headers={"content-type": "application/json"},
                        json={
                            "contents": [
                                {"role": "user", "parts": [{"text": user_message}]},
                                {"role": "model", "parts": [{"functionCall": function_call}]},
                                {"role": "function", "parts": [{"functionResponse": {"name": func_name, "response": func_result}}]}
                            ],
                            "systemInstruction": {"parts": [{"text": system_prompt}]},
                            "tools": [{"functionDeclarations": FUNCTION_DECLARATIONS}],
                            "generationConfig": {
                                "temperature": 0.7,
                                "maxOutputTokens": 500,
                            },
                        },
                    )

                    if response2.status_code == 200:
                        data2 = response2.json()
                        text = data2.get("candidates", [{}])[0].get("content", {}).get("parts", [{}])[0].get("text", "")
                        return text or "抱歉，无法生成回答。"
                    else:
                        return f"抱歉，生成回答失败。错误: {response2.status_code}"
                else:
                    # No function call, return direct text response
                    text = parts[0].get("text", "") if parts else ""
                    return text or "抱歉，我不太理解您的问题。您可以问我关于账单的问题，比如'餐饮花了多少钱？'或'最大的一笔支出是什么？'"

        except httpx.TimeoutException:
            return "抱歉，请求超时，请稍后重试。"
        except Exception as e:
            return f"抱歉，发生错误: {str(e)}"
