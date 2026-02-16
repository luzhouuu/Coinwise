"""交易描述清洗工具 - 去除支付中介前缀，保留实际商户名"""
import re
from typing import List, Tuple

# 有序的清洗规则列表，每轮按顺序匹配
# 支持嵌套前缀如 "网上消费 财付通，微信支付-商户"
_PATTERNS: List[re.Pattern] = [
    re.compile(r"^网上消费\s*"),
    re.compile(r"^财付通[，,\s]*(?:微信支付)?[-—，,\s]*"),
    re.compile(r"^支付宝[-—，,\s]*(?:消费|公用事业缴费)?[-—，,\s]*"),
    re.compile(r"^微信支付[-—，,\s]*"),
    re.compile(r"^(?:银联|云闪付)[-—，,\s]*"),
    re.compile(r"^(?:手机支付|快捷支付)[-—，,\s]*"),
    re.compile(r"^(?:网银在线|美团支付)[-—，,\s]*"),
    re.compile(r"^[，,]+\s*"),  # 兜底：清除残留的前导逗号
]

MAX_ROUNDS = 5  # 最多清洗轮数，防止意外循环


def clean_description(raw: str) -> str:
    """清洗交易描述，去除支付中介前缀。

    多轮匹配处理嵌套前缀。清洗结果为空时返回原始值。

    Args:
        raw: 原始交易描述

    Returns:
        清洗后的商户名
    """
    if not raw:
        return raw

    text = raw.strip()

    for _ in range(MAX_ROUNDS):
        changed = False
        for pattern in _PATTERNS:
            new_text = pattern.sub("", text)
            if new_text != text:
                text = new_text.strip()
                changed = True
                break  # 从头重新匹配
        if not changed:
            break

    # 清洗结果为空时返回原始值（去除前导逗号）
    fallback = raw.strip().lstrip("，,").strip()
    return text if text else (fallback or raw.strip())
