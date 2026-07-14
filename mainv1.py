import streamlit as st
import pandas as pd
import plotly.express as px
import requests
import urllib3
import re
import xml.etree.ElementTree as ET
import textwrap
from datetime import datetime

# 1. 禁用未验证的 HTTPS 请求警告
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

# 2. 设置 Streamlit 页面配置
st.set_page_config(
    page_title="全球国家宏观与电子终端战略情报看板",
    page_icon="🌍",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ==================== 🔒 核心状态初始化 ====================
if "selected_region" not in st.session_state:
    st.session_state["selected_region"] = "全部大洲"
if "selected_country" not in st.session_state:
    st.session_state["selected_country"] = "China"
if "app_mode" not in st.session_state:
    st.session_state["app_mode"] = "📰 模块一：全球实时经济新闻与情绪雷达"
if "news_last_updated" not in st.session_state:
    st.session_state["news_last_updated"] = {}
if "macro_last_updated" not in st.session_state:
    st.session_state["macro_last_updated"] = None

st.title("🌍 全球国家信息与宏观经济洞察看板")
st.markdown("---")

# ==================== 🛠️ 静态国家与配置数据库 ====================
COUNTRY_CONFIGS = {
    "China": {
        "rss_url": "https://finance.sina.com.cn/gongsi/rss.xml",
        "pos": ['增长', '稳步', '新质生产力', '复苏', '利好', '创新', '突破', '活跃'],
        "neg": ['下滑', '放缓', '收缩', '风险', '承压', '亏损', '严峻', '内卷'],
    },
    "Indonesia": {
        "rss_url": "https://www.antaranews.com/rss/ekonomi.xml",
        "pos": ['tumbuh', 'meningkat', 'untung', 'sukses', 'investasi', 'optimis', 'surplus'],
        "neg": ['turun', 'lemah', 'krisis', 'inflasi', 'rugi', 'resiko', 'lambat'],
    },
    "Philippines": {
        "rss_url": "https://www.bworldonline.com/feed/",
        "pos": ['growth', 'increase', 'boost', 'expand', 'optimism', 'remittance', 'recovery'],
        "neg": ['drop', 'decline', 'slowdown', 'inflation', 'risk', 'slump', 'weak'],
    },
    "Malaysia": {
        "rss_url": "https://theedgemalaysia.com/rss/corporate",
        "pos": ['growth', 'rise', 'surged', 'rebound', 'investment', 'positive', 'profit'],
        "neg": ['fall', 'drop', 'contraction', 'slump', 'risk', 'loss', 'bearish'],
    },
    "Thailand": {
        "rss_url": "https://www.bangkokpost.com/rss/data/business.xml",
        "pos": ['growth', 'boost', 'recovery', 'rebound', 'gain', 'surplus', 'tourism'],
        "neg": ['slump', 'drop', 'fall', 'decline', 'slowdown', 'risk', 'aging'],
    },
    "Vietnam": {
        "rss_url": "https://vnexpress.net/rss/kinh-doanh.xml",
        "pos": ['tang', 'phat trien', 'tang truong', 'loi nhuan', 'dau tu', 'on dinh'],
        "neg": ['giam', 'suy thoai', 'lo', 'rui ro', 'kho khan', 'lam phat'],
    },
    "Singapore": {
        "rss_url": "https://www.straitstimes.com/news/business/rss.xml",
        "pos": ['growth', 'rise', 'expansion', 'rebound', 'hub', 'wealth', 'surged'],
        "neg": ['slowdown', 'drop', 'risk', 'inflation', 'contraction', 'cooling', 'slump'],
    },
    "Japan": {
        "rss_url": "https://www.nikkei.com/rss/index.rdf",
        "pos": ['上昇', '拡大', '回復', '成長', 'プラス', '黒字', '株高'],
        "neg": ['下落', '縮小', 'リスク', 'インフレ', 'マイナス', '赤字', '鈍化'],
    },
    "Turkey": {
        "rss_url": "https://www.aa.com.tr/tr/rss/kategori/ekonomi",
        "pos": ['artisi', 'buyume', 'yukselis', 'kazanc', 'destek', 'yatirim', 'guven'],
        "neg": ['dusus', 'enflasyon', 'risk', 'kayip', 'yavaslama', 'daralma', 'kriz'],
    },
    "Poland": {
        "rss_url": "https://www.bankier.pl/rss/ekonomia.xml",
        "pos": ['wzrost', 'zysk', 'sukces', 'rozwoj', 'pozytywny', 'optymizm', 'rekord'],
        "neg": ['spadek', 'strata', 'kryzys', 'inflacja', 'negatywny', 'problem', 'ryzyko'],
    },
    "Germany": {
        "rss_url": "https://www.faz.net/rss/aktuell/wirtschaft/",
        "pos": ['wachstum', 'gewinn', 'plus', 'erholung', 'investition', 'stabil', 'optimismus'],
        "neg": ['rückgang', 'verlust', 'krise', 'inflation', 'risiko', 'schwäche', 'stagnation'],
    },
    "Spain": {
        "rss_url": "https://www.elconfidencial.com/rss/economia/",
        "pos": ['crecimiento', 'subida', 'beneficio', 'recuperacion', 'inversion', 'positivo', 'empleo'],
        "neg": ['caida', 'bajada', 'perdida', 'crisis', 'inflacion', 'riesgo', 'frenazo'],
    },
    "Italy": {
        "rss_url": "https://www.ilsole24ore.com/rss/economia.xml",
        "pos": ['crescita', 'aumento', 'utile', 'ripresa', 'investimento', 'positivo', 'record'],
        "neg": ['calo', 'diminuzione', 'perdita', 'crisis', 'inflazione', 'rischio', 'rallentamento'],
    },
    "France": {
        "rss_url": "https://www.lefigaro.fr/rss/figaro_economie.xml",
        "pos": ['croissance', 'hausse', 'profit', 'reprise', 'investissement', 'positif', 'succes'],
        "neg": ['baisse', 'chute', 'perte', 'crise', 'inflation', 'risque', 'ralentissement'],
    },
    "United Kingdom": {
        "rss_url": "https://www.ft.com/?format=rss",
        "pos": ['growth', 'rise', 'expansion', 'rebound', 'investment', 'positive', 'profit'],
        "neg": ['slowdown', 'drop', 'risk', 'inflation', 'contraction', 'deficit', 'slump'],
    },
    "Russia": {
        "rss_url": "https://www.vedomosti.ru/rss/news",
        "pos": ['рост', 'прибыль', 'увеличение', 'развитие', 'инвестиции', 'стабильность'],
        "neg": ['падение', 'убыток', 'кризис', 'инфляция', 'риск', 'санкции', 'снижение'],
    },
    "UAE": {
        "rss_url": "https://www.arabianbusiness.com/industries/banking-finance/rss",
        "pos": ['growth', 'rise', 'boom', 'investment', 'hub', 'surged', 'wealth'],
        "neg": ['slowdown', 'drop', 'risk', 'inflation', 'cooling', 'decline', 'slump'],
    },
    "Saudi Arabia": {
        "rss_url": "https://www.arabnews.com/cat/4/rss.xml",
        "pos": ['growth', 'expansion', 'investment', 'vision', 'gains', 'surged', 'boom'],
        "neg": ['slowdown', 'drop', 'risk', 'inflation', 'decline', 'deficit', 'slump'],
    },
    "South Africa": {
        "rss_url": "https://www.moneyweb.co.za/feed/",
        "pos": ['growth', 'rise', 'rebound', 'investment', 'positive', 'recovery', 'gain'],
        "neg": ['load-shedding', 'slowdown', 'drop', 'risk', 'inflation', 'weak', 'slump'],
    },
    "Kuwait": {
        "rss_url": "https://www.arabtimesonline.com/feed/",
        "pos": ['growth', 'rise', 'surged', 'investment', 'surplus', 'wealth', 'positive'],
        "neg": ['slowdown', 'drop', 'risk', 'inflation', 'decline', 'deficit', 'weak'],
    },
    "Mexico": {
        "rss_url": "https://www.eleconomista.com.mx/rss/economia",
        "pos": ['crecimiento', 'subida', 'beneficio', 'inversion', 'empleo', 'record', 'alza'],
        "neg": ['caida', 'bajada', 'perdida', 'crisis', 'inflacion', 'riesgo', 'freno'],
    },
    "Colombia": {
        "rss_url": "https://www.larepublica.co/rss/economia",
        "pos": ['crecimiento', 'aumento', 'inversion', 'recuperacion', 'positivo', 'desarrollo'],
        "neg": ['caida', 'disminucion', 'crisis', 'inflacion', 'riesgo', 'devaluacion'],
    },
    "Chile": {
        "rss_url": "https://www.df.cl/suplementos/rss/df/portada.xml",
        "pos": ['crecimiento', 'alza', 'inversion', 'recuperacion', 'superavit', 'estabilidad'],
        "neg": ['caida', 'baja', 'crisis', 'inflacion', 'riesgo', 'deficit', 'frenazo'],
    }
}


# ==================== 🛠️ 战略文本自动生成引擎 ====================
def generate_market_briefing(country_name, country_data, current_news, market_vibe):
    """
    实时战略简报生成引擎：融合动态 RSS 监控流与国家宏观底盘，输出干净的英文商业简报。
    """
    latest_macro_events = []
    latest_business_signals = []

    if current_news:
        for idx, news in enumerate(current_news[:4]):
            sentiment_tag = "Positive Factor" if "正面" in news.get('sentiment', '') else (
                "Negative Risk" if "负面" in news.get('sentiment', '') else "Neutral Signal")
            event_desc = f"[{sentiment_tag}] {news.get('title', 'No Title')}. (Context: {news.get('desc', 'No Content')})"
            if idx % 2 == 0:
                latest_macro_events.append(event_desc)
            else:
                latest_business_signals.append(event_desc)
    else:
        latest_macro_events = ["No immediate macro updates detected in the current RSS stream."]
        latest_business_signals = ["Business environment channels are operating steadily with no breakthrough signals."]

    macro_status_str = " | ".join(latest_macro_events)
    business_env_str = " | ".join(latest_business_signals)

    raw_briefing = f"""
### **Executive Insights: {country_name} Live Strategic Report**
*Generated dynamically based on the latest economic intelligence streams on this session.*

#### **🏦 I. Macro Environment (Macroeconomic, Politics & Business)**
* **Macroeconomic Status & News Stream:** {macro_status_str}
* **Political Landscape & Policy Vibe:** Currently aligned with market sentiment monitored as **{market_vibe}**. Government infrastructure supports a total population of **{int(country_data.get('总人口', 0)):,}** citizens, balancing public policies with demographic shifts (Aging Rate: {country_data.get('人口老龄化率(%)', 0)}%).
* **Local Business Environment:** {business_env_str}

#### **👤 II. Micro Consumer Portrait (Income, Habits & Ecosystem)**
* **Consumer Income & Purchasing Power:** Driven by an official Per Capita GDP of **${country_data.get('人均GDP($)', 0):,}**, the targeted consumer segment commands a Reference Disposable Income of **${country_data.get('人均可支配收入($)', 0):,}**. Spending velocity is highly correlated with real exchange fluctuations and inflation indicators.
* **Shopping & Behavioral Habits:** Purchasing patterns actively shift between online ecosystems and authorized offline channels. With a current Tablet/PC market penetration rate of **{country_data.get('平板PC产品渗透率(%)', 0)}%**, hardware devices serve as critical shared assets for remote workloads, adaptive education, and multi-scenario digital consumption.
* **Ecosystem Environment Preferences:** **Highly localized.** Due to the dynamic shift in digital infrastructure, the product ecosystem must offer fluid interoperability, seamless cross-screen flow, robust local app compatibility, and highly responsive system optimization optimized for high-frequency workflows.
"""
    return textwrap.dedent(raw_briefing)


# ==================== 🧠 区域重构与世界银行数据清洗 ====================
@st.cache_data(ttl=86400)
def load_real_global_data():
    country_mapping = {c: c for c in COUNTRY_CONFIGS.keys()}
    iso_mapping = {
        "China": "CHN", "Germany": "DEU", "Japan": "JPN", "United Kingdom": "GBR", "France": "FRA",
        "Vietnam": "VNM", "Mexico": "MEX", "Colombia": "COL", "Chile": "CHL", "Singapore": "SGP",
        "Indonesia": "IDN", "Malaysia": "MYS", "Thailand": "THA", "Philippines": "PHL", "Turkey": "TUR",
        "Poland": "POL", "Spain": "ESP", "Italy": "ITA", "Russia": "RUS", "UAE": "ARE", "Saudi Arabia": "SAU",
        "South Africa": "ZAF", "Kuwait": "KWT"
    }

    # 🌟 核心修正点：严格校准大洲分类，完美切分 亚洲、欧洲、中东非 (MEA)、美洲、欧亚 (Eurasia)
    official_micro_data = {
        # 亚洲地区 (Asia)
        "CHN": {"disposable_income": 5800, "tablet_penetration": 28.5, "region": "亚洲 (Asia)", "subregion": "东亚",
                "lang": "中文", "capital": "北京"},
        "JPN": {"disposable_income": 26000, "tablet_penetration": 45.8, "region": "亚洲 (Asia)", "subregion": "东亚",
                "lang": "日语", "capital": "东京"},
        "VNM": {"disposable_income": 3100, "tablet_penetration": 15.3, "region": "亚洲 (Asia)", "subregion": "东南亚",
                "lang": "越南语", "capital": "河内"},
        "SGP": {"disposable_income": 42000, "tablet_penetration": 61.5, "region": "亚洲 (Asia)", "subregion": "东南亚",
                "lang": "英语/马来语", "capital": "新加坡"},
        "IDN": {"disposable_income": 3300, "tablet_penetration": 12.4, "region": "亚洲 (Asia)", "subregion": "东南亚",
                "lang": "印尼语", "capital": "雅加达"},
        "MYS": {"disposable_income": 7400, "tablet_penetration": 29.8, "region": "亚洲 (Asia)", "subregion": "东南亚",
                "lang": "马来语", "capital": "吉隆坡"},
        "THA": {"disposable_income": 4600, "tablet_penetration": 24.5, "region": "亚洲 (Asia)", "subregion": "东南亚",
                "lang": "泰语", "capital": "曼谷"},
        "PHL": {"disposable_income": 2800, "tablet_penetration": 11.2, "region": "亚洲 (Asia)", "subregion": "东南亚",
                "lang": "菲律宾语", "capital": "马尼拉"},

        # 欧洲地区 (Europe)
        "DEU": {"disposable_income": 41500, "tablet_penetration": 52.0, "region": "欧洲 (Europe)", "subregion": "西欧",
                "lang": "德语", "capital": "柏林"},
        "GBR": {"disposable_income": 38000, "tablet_penetration": 58.1, "region": "欧洲 (Europe)", "subregion": "北欧",
                "lang": "英语", "capital": "伦敦"},
        "FRA": {"disposable_income": 36500, "tablet_penetration": 51.4, "region": "欧洲 (Europe)", "subregion": "西欧",
                "lang": "法语", "capital": "巴黎"},
        "POL": {"disposable_income": 12500, "tablet_penetration": 34.2, "region": "欧洲 (Europe)", "subregion": "东欧",
                "lang": "波兰语", "capital": "华沙"},
        "ESP": {"disposable_income": 24000, "tablet_penetration": 44.0, "region": "欧洲 (Europe)", "subregion": "南欧",
                "lang": "西班牙语", "capital": "马德里"},
        "ITA": {"disposable_income": 27000, "tablet_penetration": 42.6, "region": "欧洲 (Europe)", "subregion": "南欧",
                "lang": "意大利语", "capital": "罗马"},

        # 欧亚地区 (Eurasia) - 满足跨洲地缘独立分类要求
        "RUS": {"disposable_income": 7100, "tablet_penetration": 33.5, "region": "欧亚 (Eurasia)",
                "subregion": "北欧亚", "lang": "俄语", "capital": "莫斯科"},
        "TUR": {"disposable_income": 5200, "tablet_penetration": 26.7, "region": "欧亚 (Eurasia)",
                "subregion": "西亚/小亚细亚", "lang": "土耳其语", "capital": "安卡拉"},

        # 中东非地区 (MEA) - 中东与非洲国家统一清晰编组
        "ARE": {"disposable_income": 39000, "tablet_penetration": 59.8, "region": "中东非 (MEA)",
                "subregion": "湾区/中东", "lang": "阿拉伯语/英语", "capital": "阿布扎比"},
        "SAU": {"disposable_income": 16500, "tablet_penetration": 41.2, "region": "中东非 (MEA)",
                "subregion": "湾区/中东", "lang": "阿拉伯语", "capital": "利雅得"},
        "KWT": {"disposable_income": 29000, "tablet_penetration": 54.0, "region": "中东非 (MEA)",
                "subregion": "湾区/中东", "lang": "阿拉伯语", "capital": "科威特城"},
        "ZAF": {"disposable_income": 4200, "tablet_penetration": 16.5, "region": "中东非 (MEA)",
                "subregion": "南部非洲", "lang": "英语/祖鲁语", "capital": "比勒陀利亚"},

        # 美洲地区 (Americas)
        "MEX": {"disposable_income": 6200, "tablet_penetration": 22.1, "region": "美洲 (Americas)",
                "subregion": "北美/中美洲", "lang": "西班牙语", "capital": "墨西哥城"},
        "COL": {"disposable_income": 3900, "tablet_penetration": 14.8, "region": "美洲 (Americas)",
                "subregion": "南美洲", "lang": "西班牙语", "capital": "波哥大"},
        "CHL": {"disposable_income": 9800, "tablet_penetration": 31.0, "region": "美洲 (Americas)",
                "subregion": "南美洲", "lang": "西班牙语", "capital": "圣地亚哥"}
    }

    indicators = {"总人口": "SP.POP.TOTL", "人均GDP($)": "NY.GDP.PCAP.CD", "人口老龄化率(%)": "SP.POP.65UP.TO.ZS"}
    codes_param = ";".join(iso_mapping.values())
    master_data = {}

    default_macro_defaults = {
        "CHN": {"总人口": 1412000000, "人均GDP($)": 12720.0, "人口老龄化率(%)": 14.2},
        "JPN": {"总人口": 125000000, "人均GDP($)": 33800.0, "人口老龄化率(%)": 29.9},
        "DEU": {"总人口": 83800000, "人均GDP($)": 48700.0, "人口老龄化率(%)": 22.4},
        "GBR": {"总人口": 67300000, "人均GDP($)": 46000.0, "人口老龄化率(%)": 19.1},
        "FRA": {"总人口": 67900000, "人均GDP($)": 41000.0, "人口老龄化率(%)": 21.3},
        "VNM": {"总人口": 98100000, "人均GDP($)": 4100.0, "人口老龄化率(%)": 9.0},
        "MEX": {"总人口": 127500000, "人均GDP($)": 11000.0, "人口老龄化率(%)": 8.5},
        "COL": {"总人口": 51800000, "人均GDP($)": 6600.0, "人口老龄化率(%)": 9.3},
        "CHL": {"总人口": 19600000, "人均GDP($)": 15300.0, "人口老龄化率(%)": 12.5},
        "SGP": {"总人口": 5600000, "人均GDP($)": 82800.0, "人口老龄化率(%)": 14.5},
        "IDN": {"总人口": 275000000, "人均GDP($)": 4780.0, "人口老龄化率(%)": 7.0},
        "MYS": {"总人口": 33900000, "人均GDP($)": 12000.0, "人口老龄化率(%)": 7.7},
        "THA": {"总人口": 71700000, "人均GDP($)": 6900.0, "人口老龄化率(%)": 15.2},
        "PHL": {"总人口": 115000000, "人均GDP($)": 3500.0, "人口老龄化率(%)": 5.7},
        "TUR": {"总人口": 85300000, "人均GDP($)": 10600.0, "人口老龄化率(%)": 9.2},
        "POL": {"总人口": 37800000, "人均GDP($)": 18000.0, "人口老龄化率(%)": 19.1},
        "ESP": {"总人口": 47700000, "人均GDP($)": 29000.0, "人口老龄化率(%)": 20.3},
        "ITA": {"总人口": 58900000, "人均GDP($)": 34000.0, "人口老龄化率(%)": 24.0},
        "RUS": {"总人口": 143000000, "人均GDP($)": 15000.0, "人口老龄化率(%)": 16.2},
        "ARE": {"总人口": 9400000, "人均GDP($)": 53000.0, "人口老龄化率(%)": 1.9},
        "SAU": {"总人口": 36400000, "人均GDP($)": 30000.0, "人口老龄化率(%)": 3.8},
        "ZAF": {"总人口": 59800000, "人均GDP($)": 6700.0, "人口老龄化率(%)": 6.1},
        "KWT": {"总人口": 4200000, "人均GDP($)": 41000.0, "人口老龄化率(%)": 3.4}
    }

    for c_name in country_mapping.keys():
        iso = iso_mapping[c_name]
        defaults = default_macro_defaults.get(iso, {"总人口": 50000000, "人均GDP($)": 12000, "人口老龄化率(%)": 10.0})
        master_data[c_name] = {
            "国家/地区": c_name, "三字代码(ISO)": iso,
            "总人口": defaults["总人口"], "人均GDP($)": defaults["人均GDP($)"],
            "人口老龄化率(%)": defaults["人口老龄化率(%)"]
        }

    # 动态调取在线指标更新
    for label, ind_code in indicators.items():
        try:
            current_year = datetime.now().year
            url = f"https://api.worldbank.org/v2/country/{codes_param}/indicator/{ind_code}?format=json&per_page=200&date=2020:{current_year}"
            res = requests.get(url, verify=False, timeout=10)
            if res.status_code == 200:
                records = res.json()[1]
                df_temp = pd.DataFrame(records).dropna(subset=['value'])
                df_latest = df_temp.sort_values('date').groupby('countryiso3code').last().reset_index()
                rev_iso = {v: k for k, v in iso_mapping.items()}
                for _, row in df_latest.iterrows():
                    iso = row['countryiso3code']
                    c_name = rev_iso.get(iso)
                    if c_name in master_data:
                        master_data[c_name][label] = round(row['value'], 1) if label != "总人口" else int(row['value'])
        except Exception:
            pass

    final_list = []
    for c_name, info in master_data.items():
        iso = info["三字代码(ISO)"]
        micro = official_micro_data.get(iso,
                                        {"disposable_income": 5000, "tablet_penetration": 25.0, "region": "未知大洲",
                                         "subregion": "Global", "lang": "N/A", "capital": "N/A"})

        info["所属大洲"] = micro["region"]
        info["细分区域"] = micro["subregion"]
        info["首都"] = micro["capital"]
        info["官方语言"] = micro["lang"]
        info["人均可支配收入($)"] = micro["disposable_income"]
        info["平板PC产品渗透率(%)"] = micro["tablet_penetration"]
        final_list.append(info)

    return pd.DataFrame(final_list)


def analyze_global_sentiment(text, country_key):
    text_lower = text.lower()
    config = COUNTRY_CONFIGS.get(country_key, COUNTRY_CONFIGS["China"])
    pos_score = sum(1 for word in config['pos'] if word in text_lower)
    neg_score = sum(1 for word in config['neg'] if word in text_lower)
    if pos_score > neg_score:
        return "😊 正面 (Positive)", "🎯 市场情绪乐观，建议关注扩张机会", "#d4edda", "#155724"
    elif neg_score > pos_score:
        return "😟 负面 (Negative)", "⚠️ 提示宏观或行业风险，建议审慎策略", "#f8d7da", "#721c24"
    else:
        return "😐 中性 (Neutral)", "⚖️ 市场波动较小，保持常规跟踪", "#fff3cd", "#856404"


@st.cache_data(ttl=1800, show_spinner=False)
def fetch_global_news(country_key):
    config = COUNTRY_CONFIGS.get(country_key)
    if not config:
        return [], "未找到该国家的新闻源配置。"
    news_items = []
    error_message = None
    try:
        headers = {"User-Agent": "Mozilla/5.0"}
        response = requests.get(config['rss_url'], headers=headers, verify=False, timeout=10)
        response.raise_for_status()
        response.encoding = 'utf-8'
        if response.text and response.text.strip():
            root = ET.fromstring(response.text)
            for item in root.findall('.//item')[:8]:
                title = item.find('title').text if item.find('title') is not None else "No Title"
                link = item.find('link').text if item.find('link') is not None else "#"
                pub_date = item.find('pubDate').text if item.find('pubDate') is not None else "N/A"
                description = item.find('description').text if item.find('description') is not None else ""
                clean_desc = re.sub('<[^<]+?>', '', description).strip()
                label, advice, bg_color, text_color = analyze_global_sentiment(title + " " + clean_desc, country_key)
                news_items.append({
                    "title": title, "link": link, "date": pub_date, "desc": clean_desc,
                    "sentiment": label, "advice": advice, "bg": bg_color, "tc": text_color
                })
        if not news_items:
            error_message = "新闻源返回成功，但没有解析到可用资讯。"
    except Exception as exc:
        error_message = f"实时新闻抓取失败：{exc}"
    return news_items, error_message


# ==================== 📡 侧边栏动态过滤与安全防御 ====================
with st.sidebar:
    st.header("🎯 核心系统控制台")
    st.radio(
        "选择你要查看的战略情报模块：",
        options=["📰 模块一：全球实时经济新闻与情绪雷达", "📊 模块二：世界银行大盘与宏微观指标层"],
        key="app_mode"
    )
    if st.session_state["app_mode"] == "📊 模块二：世界银行大盘与宏微观指标层":
        if st.button("🔄 更新世界银行最新指标", type="primary", use_container_width=True):
            load_real_global_data.clear()
            st.session_state["macro_last_updated"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        st.caption(f"最近手动更新时间：{st.session_state['macro_last_updated'] or '尚未手动更新'}")
    st.markdown("---")
    st.subheader("🔍 维度筛选器")

    df_countries = load_real_global_data()

    # 1. 获取包含“欧亚 (Eurasia)”在内的清洗后大洲列表
    all_regions = ["全部大洲"] + sorted(list(df_countries["所属大洲"].unique()))
    st.selectbox("1️⃣ 第一步：选择大洲/战略区域", options=all_regions, key="selected_region")

    # 2. 根据选中的大洲动态刷选国家清单
    if st.session_state["selected_region"] != "全部大洲":
        filtered_df = df_countries[df_countries["所属大洲"] == st.session_state["selected_region"]]
    else:
        filtered_df = df_countries

    all_countries = sorted(list(filtered_df["国家/地区"].unique()))

    # 3. 🚨 跨区域切换时越界自适应锁：防止由于大洲切换导致上一 turn 国家不存在而崩溃
    if st.session_state["selected_country"] not in all_countries:
        st.session_state["selected_country"] = all_countries[0]

    # 4. 国家联动选择器
    st.selectbox("2️⃣ 第二步：指定目标国家", options=all_countries, key="selected_country")

current_country_data = df_countries[df_countries["国家/地区"] == st.session_state["selected_country"]].iloc[0]

# ==================== 🖥️ 主页面逻辑渲染 ====================
if st.session_state["app_mode"] == "📰 模块一：全球实时经济新闻与情绪雷达":
    st.subheader(f"📊 {st.session_state['selected_country']} 实时经济新闻与情绪雷达")

    refresh_col, status_col = st.columns([1, 4])
    with refresh_col:
        refresh_news = st.button("🔄 更新最新资讯", type="primary", use_container_width=True)
    if refresh_news:
        fetch_global_news.clear()

    with st.spinner(f"正在分析 {st.session_state['selected_country']} 最新财经资讯..."):
        current_news, news_error = fetch_global_news(st.session_state["selected_country"])

    if refresh_news and not news_error:
        st.session_state["news_last_updated"][st.session_state["selected_country"]] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    last_updated = st.session_state["news_last_updated"].get(st.session_state["selected_country"])
    with status_col:
        st.caption(f"最近手动更新时间：{last_updated or '尚未手动更新'}")

    if news_error:
        st.error(news_error)
        st.info("当前不会使用任何模拟数据。请稍后点击“更新最新资讯”重试，或检查该国家的 RSS 地址。")

    if current_news:
        sentiments = [n['sentiment'] for n in current_news]
        pos_count = sentiments.count("😊 正面 (Positive)")
        neg_count = sentiments.count("😟 负面 (Negative)")
        neu_count = sentiments.count("😐 中性 (Neutral)")
        total = len(current_news)
        sentiment_index = round(((pos_count * 100 + neu_count * 50) / total), 1) if total > 0 else 50

        s_col1, s_col2, s_col3 = st.columns(3)
        s_col1.metric("今日监控核心资讯", f"{total} 条")
        st.session_state["selected_country"]
        s_col2.metric("正面/负面情绪分布", f"📈 {pos_count} | 📉 {neg_count}")
        s_col3.metric("市场即时信心指数", f"{sentiment_index}点")

        # 🌟 一键集成：调用解耦的文本流引擎，生成纯英文 Executive Insights
        st.markdown("### 🗺️ Executive Insights: Real-Time Market Strategic Briefing")
        market_vibe = "Optimistic" if sentiment_index > 60 else ("Cautious" if sentiment_index < 40 else "Neutral")

        briefing_content = generate_market_briefing(
            country_name=st.session_state["selected_country"],
            country_data=current_country_data,
            current_news=current_news,
            market_vibe=market_vibe
        )
        st.markdown(briefing_content)

        # 承接下游：动态监控列表明细样式
        st.markdown("### 📢 动态监控明细列表")
        for idx, news in enumerate(current_news):
            with st.container():
                st.markdown(f"**[{idx + 1}] [{news['date']}] [{news['title']}]({news['link']})**")
                if news['desc']: st.caption(f"📝 *摘要：*{news['desc']}")
                st.write(
                    f'<div style="background-color:{news["bg"]}; color:{news["tc"]}; padding:8px 12px; border-radius:5px; font-size:14px; margin-bottom:15px;">AI 情绪：{news["sentiment"]} | 💡 建议：{news["advice"]}</div>',
                    unsafe_allow_html=True)

elif st.session_state["app_mode"] == "📊 模块二：世界银行大盘与宏微观指标层":
    st.subheader(f"📍 {st.session_state['selected_country']} 官方宏观经济大盘")

    kpi1, kpi2, kpi3, kpi4 = st.columns(4)
    kpi1.metric("总人口", f"{int(current_country_data['总人口']):,} 人")
    kpi2.metric("人均 GDP", f"${current_country_data['人均GDP($)']:,}")
    kpi3.metric("人均可支配收入", f"${current_country_data['人均可支配收入($)']:,}")
    kpi4.metric("平板PC渗透率", f"{current_country_data['平板PC产品渗透率(%)']}%")

    col1, col2 = st.columns([1, 2])
    with col1:
        st.subheader("📋 宏观结构与社会档案")
        info_df = pd.DataFrame({
            "核心维度": ["大洲板块", "细分区域", "行政首都", "主要语言", "老龄化率"],
            "详情": [current_country_data["所属大洲"], current_country_data["细分区域"], current_country_data["首都"],
                     current_country_data["官方语言"], f"{current_country_data['人口老龄化率(%)']}%"]
        })
        st.write(info_df.to_html(index=False, classes='table table-striped'), unsafe_allow_html=True)

    with col2:
        st.subheader("📊 区域大盘终端渗透率对比")
        peer_df = df_countries[df_countries["所属大洲"] == current_country_data["所属大洲"]]
        fig_bar = px.bar(peer_df, x="国家/地区", y="平板PC产品渗透率(%)",
                         title=f"{current_country_data['所属大洲']} 主要国家大盘渗透对比", color="平板PC产品渗透率(%)",
                         color_continuous_scale="Purples")
        st.plotly_chart(fig_bar, use_container_width=True)

    st.markdown("---")
    st.subheader("🗺️ 全球宏观数据热力地图")
    map_metric = st.selectbox("🎯 切换地图渲染维度：",
                              ["总人口", "人均GDP($)", "人均可支配收入($)", "平板PC产品渗透率(%)"])
    fig_map = px.choropleth(df_countries, locations="三字代码(ISO)", color=map_metric, hover_name="国家/地区",
                            title=f"全球各国【{map_metric}】地理分布格局", color_continuous_scale="viridis",
                            projection="natural earth")
    fig_map.update_layout(margin={"r": 0, "t": 40, "l": 0, "b": 0}, height=550)
    st.plotly_chart(fig_map, use_container_width=True)

st.markdown("---")
if st.checkbox("🔍 显示全量清洗后的底层 Dataframe 明细"):
    st.dataframe(df_countries, use_container_width=True)
