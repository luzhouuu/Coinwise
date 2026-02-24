"""Auto-categorization service for transactions."""

from typing import Optional
from sqlalchemy.orm import Session
from app.database import CategoryModel


# Categorization rules: category_name -> list of keywords
CATEGORY_RULES = {
    "餐饮": [
        "美团", "饿了么", "肯德基", "麦当劳", "星巴克", "瑞幸", "喜茶", "奈雪",
        "海底捞", "外卖", "餐饮", "餐厅", "食品", "咖啡", "奶茶", "火锅", "烧烤",
        "面馆", "饭店", "小吃", "便当", "盒饭", "馄饨", "包子", "饺子", "面包",
        "蛋糕", "甜品", "零食", "水果", "蔬菜", "超市", "便利店", "全家", "罗森",
        "7-11", "永辉", "盒马", "叮咚", "每日优鲜", "山姆", "Costco", "家乐福",
        "大润发", "华联", "物美", "联华", "LAWSON", "FamilyMart", "食堂",
        "必胜客", "汉堡王", "德克士", "真功夫", "吉野家", "味千拉面", "KFC",
        "McDonald", "Starbucks", "luckin", "吉祥馄饨", "金拱门", "CITYBOX",
        "壹佰米网络", "拉扎斯", "大众点评", "统一超商", "沃尔玛", "Walmart",
        "Manner", "M Stand", "蜜雪冰城", "霸王茶姬", "茶颜悦色", "CoCo", "古茗",
        "百果园", "多点", "T11", "七鲜", "朴朴", "芒逃", "Mangoway",
        # 新增关键词
        "SomeCoffee", "天宝兄弟", "马记永", "西贝", "莜面村", "湘墨轩",
        "清美鲜食", "有口福", "安达曼", "刘和园", "一尺花园", "Ginko",
        "雪兰鲜奶", "野人先生", "莱莱小笼", "老乡鸡", "混果汁", "洪大厨",
        "菜香园", "嗲团团", "七欣天", "良友金伴", "好德", "薛记炒货",
        "锅物料理", "羊肉汤", "泰式料理", "鸡煲", "饭团", "冰淇淋",
        "鲜奶铺", "小笼", "待着", "希界维", "国际蓝孩", "大理抱朴",
        "西双曼傣", "乐百年"
    ],
    "交通": [
        "滴滴", "打车", "出租", "uber", "曹操", "首汽", "神州", "嘀嗒",
        "公交", "地铁", "轨道交通", "交通卡", "公共交通", "高铁", "火车",
        "12306", "铁路", "动车", "机票", "航空", "东航", "南航", "国航",
        "海航", "春秋", "吉祥", "携程", "飞猪", "去哪儿", "加油", "中石化",
        "中石油", "停车", "ETC", "过路费", "高速", "共享单车", "摩拜",
        "哈啰", "青桔", "嘀嘀", "中国铁路网络", "蔚来", "NIO", "特斯拉",
        "Tesla", "小鹏", "理想", "比亚迪", "汽车", "4S店", "保养", "洗车",
        "高德", "海纳智行", "T3出行", "顺丰速运", "中通", "圆通", "申通",
        "韵达", "极兔", "菜鸟", "丰巢", "快递",
        # 新增关键词
        "闪送", "云游车行", "钧正网络", "京邦达", "铁塔能源", "云快充",
        "云南交投", "新能源充电", "充电桩", "上海新上铁"
    ],
    "购物": [
        "淘宝", "天猫", "京东", "拼多多", "唯品会", "网易严选", "小米有品",
        "苏宁", "国美", "得物", "闲鱼", "ZARA", "HM", "优衣库", "UNIQLO",
        "GAP", "无印良品", "MUJI", "耐克", "阿迪", "李宁", "Nike", "Adidas",
        "百货", "商场", "购物中心", "万达", "银泰", "网银在线", "天猫供应链",
        "DOUBLEZ", "屈臣氏", "丝芙兰", "名创优品", "苹果贸易", "Apple",
        "华为", "小米", "OPPO", "vivo", "戴森", "Dyson", "飞利浦", "抖音",
        "合众易宝", "唯泰精品", "华润万象", "蕉内", "宠物", "苹果电子产品",
        # 新增关键词
        "泡泡玛特", "全棉时代", "凯德", "晶品"
    ],
    "娱乐": [
        "电影", "影院", "万达影城", "CGV", "游戏", "Steam", "视频", "爱奇艺",
        "优酷", "腾讯视频", "B站", "音乐", "网易云", "QQ音乐", "KTV", "酒吧",
        "健身", "游泳", "瑜伽", "运动", "球馆", "门票", "景区", "乐园",
        "一兆韦德", "万达电影", "怪兽充电", "ClassPass", "大狗体育", "Keep",
        "足浴", "按摩", "SPA", "养生", "养生堂",
        # 新增关键词
        "海马体", "hairsalon", "照相馆", "潘多拉hair"
    ],
    "医疗": [
        "医院", "诊所", "门诊", "药房", "药店", "大药房", "挂号", "体检",
        "药品", "医药", "健康", "health", "医疗", "好大夫", "丁香", "眼科",
        "牙科", "口腔", "皮肤", "中医", "杨浦区中心医院", "健一网", "验光",
        "眼镜", "配镜"
    ],
    "住房": [
        "房租", "租金", "租房", "公寓", "寓", "朗诗寓", "物业", "水费",
        "电费", "燃气", "煤气", "暖气", "装修", "家具", "家电", "家居",
        "宜家", "维修", "保洁", "家政", "搬家", "电信", "移动", "联通",
        "宽带", "一网通办缴费平台", "物业管理处", "自如", "愚源名邸",
        "房屋经营", "宝地宝泉", "国网", "电力公司", "供电", "燃气公司",
        "水务", "自来水", "松下电器", "美凯龙", "居然之家",
        # 新增关键词
        "城投水"
    ],
    "通讯": [
        "话费", "充值", "流量", "套餐", "中国移动", "中国电信", "中国联通",
        "手机", "电话", "通讯", "iCloud", "Apple", "云服务", "云上贵州",
        "云上艾珀", "迅鸟科技"
    ],
    "旅游": [
        "酒店", "宾馆", "民宿", "住宿", "hotel", "Airbnb", "途家", "旅游",
        "旅行", "度假", "景点", "签证", "护照", "马蜂窝", "穷游", "阿斯兰航空",
        "中先国际", "希尔顿", "万豪", "洲际", "香格里拉", "凯悦", "汉庭",
        "如家", "锦江", "华住", "亚朵", "橙庐", "CHENGLU", "大昭寺"
    ],
    "金融": [
        "转账", "汇款", "提现", "还款", "理财", "基金", "股票", "证券",
        "投资", "保险", "人寿", "财险", "车险", "贷款", "借款", "分期",
        "手续费", "服务费", "年费", "银行", "ATM", "取现", "预借现金",
        "相互宝", "平安财产保险", "中国平安", "WorldPay", "Payment Asia",
        # 新增关键词
        "信用卡中心", "上海银行"
    ],
    "教育": [
        "学费", "培训", "课程", "教育", "书籍", "图书", "书店", "当当",
        "知识付费", "得到", "知乎", "网课", "考试", "学校", "大学", "学院"
    ]
}


class Categorizer:
    """Service for auto-categorizing transactions based on description."""

    def __init__(self, db: Session):
        self.db = db
        self._category_cache: dict[str, int] = {}
        self._load_categories()

    def _load_categories(self):
        """Load category name to ID mapping."""
        categories = self.db.query(CategoryModel).all()
        self._category_cache = {c.name: c.id for c in categories}

    def categorize(self, description: str) -> Optional[int]:
        """
        Determine category ID based on transaction description.

        Returns:
            Category ID if a match is found, None otherwise.
        """
        if not description:
            return None

        description_lower = description.lower()

        for category_name, keywords in CATEGORY_RULES.items():
            if category_name not in self._category_cache:
                continue

            for keyword in keywords:
                if keyword.lower() in description_lower:
                    return self._category_cache[category_name]

        # Return "其他" if no match found
        return self._category_cache.get("其他")
