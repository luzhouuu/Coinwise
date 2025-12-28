"""配置管理模块"""
import os
from dotenv import load_dotenv

load_dotenv()


class Config:
    """应用配置"""

    # Firefly III
    FIREFLY_API_URL = os.getenv("FIREFLY_API_URL", "http://www.joelu.cn:20006/api/v1")
    FIREFLY_API_TOKEN = os.getenv("FIREFLY_API_TOKEN", "")

    # Email accounts
    EMAIL_IMAP_SERVER = os.getenv("EMAIL_IMAP_SERVER", "imap.qq.com")

    # 支持多个邮箱账户
    EMAIL_ACCOUNTS = []
    for i in range(1, 10):
        username = os.getenv(f"EMAIL_USERNAME_{i}")
        password = os.getenv(f"EMAIL_PASSWORD_{i}")
        if username and password:
            EMAIL_ACCOUNTS.append({
                "username": username,
                "password": password
            })

    # Default source account name in Firefly III
    DEFAULT_SOURCE_NAME = "家庭支出"
