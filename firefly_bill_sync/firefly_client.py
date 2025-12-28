"""Firefly III API 客户端"""
import json
import requests
from typing import List, Dict, Optional
from datetime import datetime
import pandas as pd

from .config import Config
from .categorizer import categorize


class FireflyClient:
    """Firefly III API 客户端"""

    def __init__(self, api_url: str = None, api_token: str = None):
        self.api_url = api_url or Config.FIREFLY_API_URL
        self.api_token = api_token or Config.FIREFLY_API_TOKEN
        self.headers = {
            'accept': 'application/vnd.api+json',
            'Content-Type': 'application/json',
            'Authorization': f'Bearer {self.api_token}'
        }

    def create_transaction(
        self,
        date: str,
        amount: float,
        description: str,
        category_name: str = None,
        source_name: str = None,
        transaction_type: str = "withdrawal",
        tags: List[str] = None,
        notes: str = ""
    ) -> Optional[Dict]:
        """
        创建交易记录

        Args:
            date: 交易日期 (YYYY-MM-DD)
            amount: 金额
            description: 交易描述
            category_name: 分类名称（如不提供则自动分类）
            source_name: 来源账户名称
            transaction_type: 交易类型（withdrawal/deposit/transfer）
            tags: 标签列表
            notes: 备注

        Returns:
            API 响应 或 None
        """
        if category_name is None:
            category_name = categorize(description)

        if source_name is None:
            source_name = Config.DEFAULT_SOURCE_NAME

        payload = {
            "error_if_duplicate_hash": False,
            "apply_rules": False,
            "fire_webhooks": True,
            "transactions": [{
                "type": transaction_type,
                "date": date,
                "amount": str(amount),
                "description": description,
                "currency_code": "CNY",
                "category_name": category_name,
                "source_name": source_name,
                "tags": tags,
                "notes": notes
            }]
        }

        try:
            response = requests.post(
                f"{self.api_url}/transactions",
                headers=self.headers,
                data=json.dumps(payload)
            )
            if response.status_code in [200, 201]:
                print(f"创建成功: {date} | {amount} | {description}")
                return response.json()
            else:
                print(f"创建失败: {response.status_code} - {response.text}")
                return None
        except Exception as e:
            print(f"请求错误: {e}")
            return None

    def batch_create_transactions(self, df: pd.DataFrame) -> int:
        """
        批量创建交易记录

        Args:
            df: DataFrame with columns: date, amount, description, (optional) category

        Returns:
            成功创建的记录数
        """
        success_count = 0
        for _, row in df.iterrows():
            category = row.get("category") if "category" in df.columns else None
            result = self.create_transaction(
                date=row["date"],
                amount=row["amount"],
                description=row["description"],
                category_name=category
            )
            if result:
                success_count += 1
        return success_count

    def get_transactions(
        self,
        start_date: str = None,
        end_date: str = None,
        limit: int = 100
    ) -> pd.DataFrame:
        """
        获取交易记录

        Args:
            start_date: 开始日期 (YYYY-MM-DD)
            end_date: 结束日期 (YYYY-MM-DD)
            limit: 返回记录数限制

        Returns:
            交易记录 DataFrame
        """
        params = {"limit": limit}
        if start_date:
            params["start"] = start_date
        if end_date:
            params["end"] = end_date

        try:
            response = requests.get(
                f"{self.api_url}/transactions",
                headers=self.headers,
                params=params
            )
            if response.status_code == 200:
                data = response.json()
                return self._parse_transactions_response(data)
            else:
                print(f"获取失败: {response.status_code}")
                return pd.DataFrame()
        except Exception as e:
            print(f"请求错误: {e}")
            return pd.DataFrame()

    def _parse_transactions_response(self, data: Dict) -> pd.DataFrame:
        """解析 API 响应为 DataFrame"""
        records = []
        for item in data.get("data", []):
            attrs = item.get("attributes", {})
            transactions = attrs.get("transactions", [])
            for tx in transactions:
                records.append({
                    "id": item.get("id"),
                    "date": tx.get("date"),
                    "amount": float(tx.get("amount", 0)),
                    "description": tx.get("description"),
                    "category": tx.get("category_name"),
                    "type": tx.get("type"),
                    "source": tx.get("source_name"),
                    "destination": tx.get("destination_name"),
                    "tags": tx.get("tags", [])
                })
        return pd.DataFrame(records)

    def get_categories(self) -> List[Dict]:
        """获取所有分类"""
        try:
            response = requests.get(
                f"{self.api_url}/categories",
                headers=self.headers
            )
            if response.status_code == 200:
                data = response.json()
                return [
                    {"id": item["id"], "name": item["attributes"]["name"]}
                    for item in data.get("data", [])
                ]
            return []
        except Exception as e:
            print(f"获取分类失败: {e}")
            return []

    def get_budgets(self) -> List[Dict]:
        """获取所有预算"""
        try:
            response = requests.get(
                f"{self.api_url}/budgets",
                headers=self.headers
            )
            if response.status_code == 200:
                data = response.json()
                return data.get("data", [])
            return []
        except Exception as e:
            print(f"获取预算失败: {e}")
            return []

    def get_summary(self, start_date: str, end_date: str) -> Dict:
        """
        获取指定日期范围的汇总数据

        Returns:
            包含收入、支出、转账等汇总数据的字典
        """
        try:
            response = requests.get(
                f"{self.api_url}/summary/basic",
                headers=self.headers,
                params={"start": start_date, "end": end_date}
            )
            if response.status_code == 200:
                return response.json()
            return {}
        except Exception as e:
            print(f"获取汇总失败: {e}")
            return {}

    def transaction_exists(self, date: str, amount: float, description: str) -> bool:
        """
        检查交易是否已存在（用于去重）

        Args:
            date: 交易日期
            amount: 金额
            description: 交易描述

        Returns:
            True 如果交易已存在
        """
        try:
            # 搜索同一天的交易
            response = requests.get(
                f"{self.api_url}/transactions",
                headers=self.headers,
                params={"start": date, "end": date, "limit": 100}
            )
            if response.status_code == 200:
                data = response.json()
                for item in data.get("data", []):
                    for tx in item.get("attributes", {}).get("transactions", []):
                        tx_amount = abs(float(tx.get("amount", 0)))
                        tx_desc = tx.get("description", "")
                        # 匹配金额和描述
                        if abs(tx_amount - amount) < 0.01 and tx_desc == description:
                            return True
            return False
        except Exception as e:
            print(f"检查重复失败: {e}")
            return False

    def find_and_delete_transaction(self, date: str, amount: float, description: str) -> bool:
        """
        查找并删除匹配的交易（用于处理退款）

        Args:
            date: 原交易日期附近
            amount: 原交易金额（正数）
            description: 交易描述

        Returns:
            True 如果成功删除
        """
        try:
            # 搜索最近30天内的交易
            from datetime import datetime, timedelta
            end_date = datetime.strptime(date, "%Y-%m-%d")
            start_date = end_date - timedelta(days=60)

            response = requests.get(
                f"{self.api_url}/transactions",
                headers=self.headers,
                params={
                    "start": start_date.strftime("%Y-%m-%d"),
                    "end": end_date.strftime("%Y-%m-%d"),
                    "limit": 200
                }
            )

            if response.status_code == 200:
                data = response.json()
                for item in data.get("data", []):
                    tx_id = item.get("id")
                    for tx in item.get("attributes", {}).get("transactions", []):
                        tx_amount = abs(float(tx.get("amount", 0)))
                        tx_desc = tx.get("description", "")
                        # 匹配金额和描述（描述可能略有不同，用包含关系）
                        if abs(tx_amount - amount) < 0.01 and (
                            tx_desc == description or
                            description in tx_desc or
                            tx_desc in description
                        ):
                            # 删除这笔交易
                            return self.delete_transaction(tx_id)
            return False
        except Exception as e:
            print(f"查找删除失败: {e}")
            return False

    def delete_transaction(self, transaction_id: str) -> bool:
        """删除交易"""
        try:
            response = requests.delete(
                f"{self.api_url}/transactions/{transaction_id}",
                headers=self.headers
            )
            if response.status_code in [200, 204]:
                print(f"    删除交易成功: {transaction_id}")
                return True
            else:
                print(f"    删除失败: {response.status_code}")
                return False
        except Exception as e:
            print(f"删除请求错误: {e}")
            return False
