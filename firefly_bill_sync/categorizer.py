"""交易分类器"""
from typing import Optional


# 分类规则定义
CATEGORY_RULES = {
    "Daily Necessities": ["山姆", "水费", "电费", "燃气", "物业", "超市", "便利店"],
    "Dining": ["餐厅", "饭", "食", "饮", "酒", "大众点评", "美团", "饿了么", "拉扎斯", "麦当劳", "肯德基", "星巴克", "瑞幸", "LAWSON", "全家"],
    "Travel": ["携程", "飞猫", "酒店", "机票", "旅行", "滴滴", "出行", "打车", "高铁", "火车票"],
    "Clothing": ["比斯特", "衣", "服", "鞋", "裤", "优衣库", "ZARA", "H&M"],
    "Entertainment": ["电影", "音乐", "娱乐", "游戏", "KTV", "网易云", "爱奇艺", "腾讯视频", "B站"],
    "Pets": ["宠物", "猫", "狗", "宠"],
    "Shopping": ["京东", "淘宝", "天猫", "拼多多", "网银在线"],
    "Healthcare": ["医院", "药店", "医疗", "体检", "牙科"],
    "Education": ["教育", "培训", "书店", "课程"],
}


def categorize(description: str) -> str:
    """
    根据交易描述自动分类

    Args:
        description: 交易描述

    Returns:
        分类名称
    """
    if not description:
        return "Other"

    description_lower = description.lower()

    for category, keywords in CATEGORY_RULES.items():
        for keyword in keywords:
            if keyword.lower() in description_lower:
                return category

    return "Other"


def add_category_rule(category: str, keyword: str):
    """添加新的分类规则"""
    if category not in CATEGORY_RULES:
        CATEGORY_RULES[category] = []
    if keyword not in CATEGORY_RULES[category]:
        CATEGORY_RULES[category].append(keyword)


def get_all_categories() -> list:
    """获取所有分类"""
    return list(CATEGORY_RULES.keys()) + ["Other"]
