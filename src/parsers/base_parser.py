"""基础账单解析器"""
from abc import ABC, abstractmethod
from typing import List, Dict
import pandas as pd


class BaseBillParser(ABC):
    """账单解析器基类"""

    # 邮件主题关键字，用于匹配
    SUBJECT_KEYWORDS: List[str] = []

    @abstractmethod
    def parse(self, html_content: str, email_date: str = None) -> pd.DataFrame:
        """
        解析 HTML 账单内容

        Args:
            html_content: HTML 内容
            email_date: 邮件日期

        Returns:
            DataFrame with columns: date, amount, description
        """
        pass

    @classmethod
    def get_subject_keywords(cls) -> List[str]:
        """获取邮件主题关键字"""
        return cls.SUBJECT_KEYWORDS
