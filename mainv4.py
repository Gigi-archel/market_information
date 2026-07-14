import streamlit as st
import pandas as pd
import plotly.express as px
import requests
import urllib3
import re
import xml.etree.ElementTree as ET
import textwrap
from datetime import datetime, timedelta, timezone
from email.utils import parsedate_to_datetime
from urllib.parse import quote_plus, urlparse

# 1. 禁用未验证的 HTTPS 请求警告
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

# 2. 设置 Streamlit 页面配置
st.set_page_config(
    page_title="全球国家宏观与电子终端战略情报看板",
    page_icon="◈",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ==================== 🎨 时尚科技简约主题 ====================
px.defaults.template = "plotly_dark"
px.defaults.color_continuous_scale = "Turbo"

st.markdown("""
<style>
    :root {
        --bg: #07101f;
        --panel: rgba(14, 27, 48, 0.72);
        --panel-solid: #0e1b30;
        --line: rgba(148, 163, 184, 0.16);
        --text: #e8f0fb;
        --muted: #91a4bf;
        --cyan: #22d3ee;
        --blue: #4f7cff;
        --violet: #8b5cf6;
    }

    html, body, [class*="css"] {
        font-family: Inter, "SF Pro Display", "Segoe UI", "Microsoft YaHei", sans-serif;
    }

    .stApp {
        color: var(--text);
        background:
            radial-gradient(circle at 78% 5%, rgba(79, 124, 255, .16), transparent 28rem),
            radial-gradient(circle at 12% 78%, rgba(34, 211, 238, .08), transparent 24rem),
            var(--bg);
    }

    .stApp::before {
        content: "";
        position: fixed;
        inset: 0;
        pointer-events: none;
        opacity: .22;
        background-image:
            linear-gradient(rgba(148,163,184,.035) 1px, transparent 1px),
            linear-gradient(90deg, rgba(148,163,184,.035) 1px, transparent 1px);
        background-size: 36px 36px;
        mask-image: linear-gradient(to bottom, black, transparent 82%);
    }

    [data-testid="stHeader"] {
        background: rgba(7, 16, 31, .68);
        backdrop-filter: blur(18px);
        border-bottom: 1px solid var(--line);
    }

    [data-testid="stSidebar"] {
        background: rgba(9, 19, 35, .94);
        border-right: 1px solid var(--line);
    }

    [data-testid="stSidebar"] > div:first-child {
        padding-top: 2rem;
    }

    .block-container {
        max-width: 1480px;
        padding-top: 2.25rem;
        padding-bottom: 4rem;
    }

    h1 {
        font-size: clamp(2rem, 3vw, 3.25rem) !important;
        letter-spacing: -.045em !important;
        font-weight: 760 !important;
        background: linear-gradient(95deg, #ffffff 10%, #8de8ff 58%, #8ba8ff 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
    }

    h2, h3 {
        color: #f5f8ff !important;
        letter-spacing: -.025em !important;
    }

    p, label, [data-testid="stCaptionContainer"] {
        color: var(--muted);
    }

    hr {
        border: 0 !important;
        height: 1px !important;
        background: linear-gradient(90deg, transparent, rgba(34,211,238,.36), transparent) !important;
        margin: 1.4rem 0 2rem !important;
    }

    [data-testid="stMetric"] {
        min-height: 116px;
        padding: 1.15rem 1.25rem;
        border: 1px solid var(--line);
        border-radius: 18px;
        background: linear-gradient(145deg, rgba(18, 35, 61, .92), rgba(10, 22, 40, .78));
        box-shadow: 0 18px 45px rgba(0, 0, 0, .2), inset 0 1px 0 rgba(255,255,255,.035);
        transition: transform .2s ease, border-color .2s ease;
    }

    [data-testid="stMetric"]:hover {
        transform: translateY(-2px);
        border-color: rgba(34, 211, 238, .34);
    }

    [data-testid="stMetricLabel"] { color: #8fa4c1; }
    [data-testid="stMetricValue"] {
        color: #f7fbff;
        font-weight: 700;
        letter-spacing: -.035em;
    }

    .stButton > button {
        border: 1px solid rgba(34, 211, 238, .42) !important;
        border-radius: 12px !important;
        color: #effcff !important;
        background: linear-gradient(115deg, rgba(25, 86, 126, .72), rgba(61, 65, 154, .78)) !important;
        box-shadow: 0 8px 24px rgba(21, 83, 125, .2) !important;
        font-weight: 650 !important;
        transition: all .2s ease !important;
    }

    .stButton > button:hover {
        border-color: var(--cyan) !important;
        box-shadow: 0 10px 30px rgba(34, 211, 238, .2) !important;
        transform: translateY(-1px);
    }

    [data-baseweb="select"] > div,
    [data-baseweb="input"] > div {
        color: var(--text) !important;
        background: rgba(14, 27, 48, .84) !important;
        border-color: var(--line) !important;
        border-radius: 12px !important;
    }

    [data-testid="stPlotlyChart"],
    [data-testid="stDataFrame"],
    .stTable {
        overflow: hidden;
        border: 1px solid var(--line);
        border-radius: 18px;
        background: var(--panel);
        box-shadow: 0 20px 50px rgba(0, 0, 0, .16);
    }

    [data-testid="stAlert"] {
        border-radius: 14px;
        border: 1px solid var(--line);
        background: rgba(14, 27, 48, .86);
    }

    a { color: #68ddf4 !important; text-decoration: none !important; }
    a:hover { color: #a4efff !important; }

    .tech-eyebrow {
        display: inline-flex;
        align-items: center;
        gap: .55rem;
        margin-bottom: .35rem;
        padding: .38rem .7rem;
        border: 1px solid rgba(34, 211, 238, .23);
        border-radius: 999px;
        color: #8eeaff;
        background: rgba(34, 211, 238, .055);
        font-size: .72rem;
        font-weight: 700;
        letter-spacing: .14em;
        text-transform: uppercase;
    }

    .tech-eyebrow::before {
        content: "";
        width: 6px;
        height: 6px;
        border-radius: 50%;
        background: #34d399;
        box-shadow: 0 0 12px #34d399;
    }

    .dashboard-subtitle {
        max-width: 760px;
        margin-top: -.5rem;
        color: #8397b3;
        font-size: 1rem;
        line-height: 1.7;
    }

    @media (max-width: 768px) {
        .block-container { padding: 1.4rem 1rem 3rem; }
        [data-testid="stMetric"] { min-height: 100px; }
    }
</style>
""", unsafe_allow_html=True)


def style_chart(fig, height=None):
    """统一图表为透明、低噪声的科技深色视觉。"""
    fig.update_layout(
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        font=dict(color="#a9bad0", family="Inter, Segoe UI, Microsoft YaHei"),
        title_font=dict(color="#f5f8ff", size=17),
        coloraxis_colorbar=dict(outlinewidth=0, tickfont=dict(color="#91a4bf")),
        margin=dict(l=18, r=18, t=58, b=18),
        hoverlabel=dict(bgcolor="#101f36", bordercolor="#334a68", font_color="#f5f8ff")
    )
    fig.update_xaxes(showgrid=False, zeroline=False, linecolor="rgba(148,163,184,.12)")
    fig.update_yaxes(gridcolor="rgba(148,163,184,.10)", zeroline=False)
    if height:
        fig.update_layout(height=height)
    return fig

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
if "selected_macro_year" not in st.session_state:
    st.session_state["selected_macro_year"] = datetime.now().year - 2

st.markdown('<div class="tech-eyebrow">GLOBAL INTELLIGENCE · LIVE</div>', unsafe_allow_html=True)
st.title("全球市场战略情报中心")
st.markdown('<p class="dashboard-subtitle">聚合全球财经资讯、市场情绪与宏观指标，以清晰的数据视角辅助区域洞察和终端战略决策。</p>', unsafe_allow_html=True)
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

# 每个国家配置“主来源 + 备用来源”。主来源无响应、非 XML 或无有效条目时自动切换。
# source_url 用于界面溯源，url 为可机器读取的 RSS / Atom / RDF 地址。
NEWS_SOURCES = {
    "China": [
        {"name": "新浪财经", "url": "https://rss.sina.com.cn/news/china/focus15.xml", "source_url": "https://finance.sina.com.cn"},
        {"name": "南华早报 · 中国经济", "url": "https://news.google.com/rss/search?q=site%3Ascmp.com%20China%20economy&hl=en-US&gl=US&ceid=US%3Aen", "source_url": "https://www.scmp.com/economy/china-economy"}],
    "Indonesia": [
        {"name": "ANTARA Economy", "url": "https://www.antaranews.com/rss/ekonomi", "source_url": "https://www.antaranews.com/ekonomi"},
        {"name": "Detik Finance", "url": "https://finance.detik.com/rss", "source_url": "https://finance.detik.com"}],
    "Philippines": [
        {"name": "BusinessWorld", "url": "https://www.bworldonline.com/feed/", "source_url": "https://www.bworldonline.com"},
        {"name": "The Philippine Star · Business", "url": "https://www.philstar.com/rss/business", "source_url": "https://www.philstar.com/business"}],
    "Malaysia": [
        {"name": "Malay Mail · Money", "url": "https://www.malaymail.com/feed/rss/money", "source_url": "https://www.malaymail.com/news/money"},
        {"name": "The Edge Malaysia", "url": "https://news.google.com/rss/search?q=site%3Atheedgemalaysia.com%20economy&hl=en-US&gl=US&ceid=US%3Aen", "source_url": "https://theedgemalaysia.com"}],
    "Thailand": [
        {"name": "Bangkok Post · Business", "url": "https://www.bangkokpost.com/rss/data/business.xml", "source_url": "https://www.bangkokpost.com/business"},
        {"name": "The Nation Thailand · Business", "url": "https://news.google.com/rss/search?q=site%3Anationthailand.com%20business&hl=en-US&gl=US&ceid=US%3Aen", "source_url": "https://www.nationthailand.com/business"}],
    "Vietnam": [
        {"name": "VnExpress · Kinh doanh", "url": "https://vnexpress.net/rss/kinh-doanh.rss", "source_url": "https://vnexpress.net/kinh-doanh"},
        {"name": "Viet Nam News · Economy", "url": "https://vietnamnews.vn/rss/economy.rss", "source_url": "https://vietnamnews.vn/economy"}],
    "Singapore": [
        {"name": "The Straits Times · Business", "url": "https://www.straitstimes.com/news/business/rss.xml", "source_url": "https://www.straitstimes.com/business"},
        {"name": "Channel NewsAsia · Business", "url": "https://www.channelnewsasia.com/api/v1/rss-outbound-feed?_format=xml&category=6936", "source_url": "https://www.channelnewsasia.com/business"}],
    "Japan": [
        {"name": "NHK · Business", "url": "https://www3.nhk.or.jp/rss/news/cat5.xml", "source_url": "https://www3.nhk.or.jp/news/business.html"},
        {"name": "The Japan Times", "url": "https://www.japantimes.co.jp/feed/", "source_url": "https://www.japantimes.co.jp/news_category/business"}],
    "Turkey": [
        {"name": "Anadolu Agency · Economy", "url": "https://www.aa.com.tr/en/rss/default?cat=economy", "source_url": "https://www.aa.com.tr/en/economy"},
        {"name": "Daily Sabah · Economy", "url": "https://www.dailysabah.com/rssFeed/12", "source_url": "https://www.dailysabah.com/business/economy"}],
    "Poland": [
        {"name": "Bankier.pl · Economy", "url": "https://www.bankier.pl/rss/wiadomosci.xml", "source_url": "https://www.bankier.pl/wiadomosci"},
        {"name": "Notes from Poland · Business", "url": "https://notesfrompoland.com/category/business/feed/", "source_url": "https://notesfrompoland.com/category/business"}],
    "Germany": [
        {"name": "FAZ · Wirtschaft", "url": "https://www.faz.net/rss/aktuell/wirtschaft/", "source_url": "https://www.faz.net/aktuell/wirtschaft"},
        {"name": "Deutsche Welle · Business", "url": "https://rss.dw.com/rdf/rss-en-bus", "source_url": "https://www.dw.com/en/business/s-1431"}],
    "Spain": [
        {"name": "El País · Economía", "url": "https://feeds.elpais.com/mrss-s/pages/ep/site/elpais.com/section/economia/portada", "source_url": "https://elpais.com/economia"},
        {"name": "El Confidencial · Economía", "url": "https://news.google.com/rss/search?q=site%3Aelconfidencial.com%20economia&hl=es&gl=ES&ceid=ES%3Aes", "source_url": "https://www.elconfidencial.com/economia"}],
    "Italy": [
        {"name": "ANSA · Economia", "url": "https://www.ansa.it/sito/notizie/economia/economia_rss.xml", "source_url": "https://www.ansa.it/sito/notizie/economia"},
        {"name": "Rai News", "url": "https://www.rainews.it/rss/tutti", "source_url": "https://www.rainews.it"}],
    "France": [
        {"name": "Le Figaro · Économie", "url": "https://www.lefigaro.fr/rss/figaro_economie.xml", "source_url": "https://www.lefigaro.fr/economie"},
        {"name": "France 24 · Economy", "url": "https://www.france24.com/en/economy/rss", "source_url": "https://www.france24.com/en/economy"}],
    "United Kingdom": [
        {"name": "Financial Times", "url": "https://www.ft.com/?format=rss", "source_url": "https://www.ft.com"},
        {"name": "BBC · Business", "url": "https://feeds.bbci.co.uk/news/business/rss.xml", "source_url": "https://www.bbc.com/news/business"}],
    "Russia": [
        {"name": "Vedomosti", "url": "https://www.vedomosti.ru/rss/news", "source_url": "https://www.vedomosti.ru"},
        {"name": "TASS", "url": "https://tass.com/rss/v2.xml", "source_url": "https://tass.com/economy"}],
    "UAE": [
        {"name": "The National · Business", "url": "https://www.thenationalnews.com/arc/outboundfeeds/rss/category/business/?outputType=xml", "source_url": "https://www.thenationalnews.com/business"},
        {"name": "Arabian Business", "url": "https://news.google.com/rss/search?q=site%3Aarabianbusiness.com%20UAE%20business&hl=en-US&gl=AE&ceid=AE%3Aen", "source_url": "https://www.arabianbusiness.com"}],
    "Saudi Arabia": [
        {"name": "Arab News · Business", "url": "https://www.arabnews.com/cat/4/rss.xml", "source_url": "https://www.arabnews.com/economy"},
        {"name": "Saudi Gazette", "url": "https://news.google.com/rss/search?q=site%3Asaudigazette.com.sa%20economy&hl=en-US&gl=SA&ceid=SA%3Aen", "source_url": "https://saudigazette.com.sa"}],
    "South Africa": [
        {"name": "Moneyweb", "url": "https://www.moneyweb.co.za/feed/", "source_url": "https://www.moneyweb.co.za"},
        {"name": "BusinessTech", "url": "https://news.google.com/rss/search?q=site%3Abusinesstech.co.za%20economy&hl=en-US&gl=ZA&ceid=ZA%3Aen", "source_url": "https://businesstech.co.za/news"}],
    "Kuwait": [
        {"name": "Arab Times Kuwait", "url": "https://news.google.com/rss/search?q=site%3Aarabtimesonline.com%20Kuwait%20business&hl=en-US&gl=KW&ceid=KW%3Aen", "source_url": "https://www.arabtimesonline.com"},
        {"name": "Kuwait Times", "url": "https://news.google.com/rss/search?q=site%3Akuwaittimes.com%20economy&hl=en-US&gl=KW&ceid=KW%3Aen", "source_url": "https://kuwaittimes.com"}],
    "Mexico": [
        {"name": "El Economista · Economía", "url": "https://www.eleconomista.com.mx/rss/economia", "source_url": "https://www.eleconomista.com.mx/economia"},
        {"name": "Mexico News Daily · Business", "url": "https://mexiconewsdaily.com/category/business/feed/", "source_url": "https://mexiconewsdaily.com/category/business"}],
    "Colombia": [
        {"name": "La República · Economía", "url": "https://www.larepublica.co/rss/economia", "source_url": "https://www.larepublica.co/economia"},
        {"name": "Portafolio · Economía", "url": "https://news.google.com/rss/search?q=site%3Aportafolio.co%20economia&hl=es&gl=CO&ceid=CO%3Aes-419", "source_url": "https://www.portafolio.co/economia"}],
    "Chile": [
        {"name": "Diario Financiero", "url": "https://news.google.com/rss/search?q=site%3Adf.cl%20economia&hl=es&gl=CL&ceid=CL%3Aes-419", "source_url": "https://www.df.cl"},
        {"name": "Emol · Economía", "url": "https://news.google.com/rss/search?q=site%3Aemol.com%20economia&hl=es&gl=CL&ceid=CL%3Aes-419", "source_url": "https://www.emol.com/economia"}]
}


# ==================== 🛠️ 战略文本自动生成引擎 ====================
def format_number(value, decimals=0, prefix="", suffix=""):
    """安全格式化在线指标；缺失值统一显示 N/A。"""
    if value is None or pd.isna(value):
        return "N/A"
    return f"{prefix}{float(value):,.{decimals}f}{suffix}"


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
            event_desc = (f"[{sentiment_tag}] {news.get('title_en', news.get('title', 'No Title'))}. "
                          f"(Context: {news.get('desc_en', news.get('desc', 'No Content'))})")
            if idx % 2 == 0:
                latest_macro_events.append(event_desc)
            else:
                latest_business_signals.append(event_desc)
    else:
        latest_macro_events = ["No immediate macro updates detected in the current RSS stream."]
        latest_business_signals = ["Business environment channels are operating steadily with no breakthrough signals."]

    macro_status_str = " | ".join(latest_macro_events)
    business_env_str = " | ".join(latest_business_signals)

    population_text = format_number(country_data.get('总人口'), 0)
    aging_text = format_number(country_data.get('人口老龄化率(%)'), 1, suffix="%")
    gdp_text = format_number(country_data.get('人均GDP($)'), 0, prefix="$")
    income_text = format_number(country_data.get('人均可支配收入($)'), 0, prefix="$")

    raw_briefing = f"""
### **Executive Insights: {country_name} Live Strategic Report**
*Generated dynamically based on the latest economic intelligence streams on this session.*

#### **🏦 I. Macro Environment (Macroeconomic, Politics & Business)**
* **Macroeconomic Status & News Stream:** {macro_status_str}
* **Political Landscape & Policy Vibe:** Currently aligned with market sentiment monitored as **{market_vibe}**. The selected World Bank year reports a total population of **{population_text}** citizens, with an aging rate of **{aging_text}**.
* **Local Business Environment:** {business_env_str}

#### **👤 II. Micro Consumer Portrait (Income, Habits & Ecosystem)**
* **Consumer Income & Purchasing Power:** Driven by an official Per Capita GDP of **{gdp_text}**, the targeted consumer segment commands a Reference Disposable Income of **{income_text}**. Spending velocity is highly correlated with real exchange fluctuations and inflation indicators.
* **Shopping & Behavioral Habits:** Purchasing patterns actively shift between online ecosystems and authorized offline channels. With a current Tablet/PC market penetration rate of **{country_data.get('平板PC产品渗透率(%)', 0)}%**, hardware devices serve as critical shared assets for remote workloads, adaptive education, and multi-scenario digital consumption.
* **Ecosystem Environment Preferences:** **Highly localized.** Due to the dynamic shift in digital infrastructure, the product ecosystem must offer fluid interoperability, seamless cross-screen flow, robust local app compatibility, and highly responsive system optimization optimized for high-frequency workflows.
"""
    return textwrap.dedent(raw_briefing)


# ==================== 🧠 区域重构与世界银行数据清洗 ====================
@st.cache_data(ttl=86400, show_spinner=False)
def load_real_global_data(selected_year):
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
        "TUR": {"disposable_income": 5200, "tablet_penetration": 26.7, "region": "欧洲 (Europe)",
                "subregion": "东南欧/小亚细亚", "lang": "土耳其语", "capital": "安卡拉"},

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

    for c_name in country_mapping.keys():
        iso = iso_mapping[c_name]
        master_data[c_name] = {
            "国家/地区": c_name, "三字代码(ISO)": iso,
            "数据年份": selected_year,
            "总人口": None, "人均GDP($)": None, "人口老龄化率(%)": None
        }

    # 动态调取在线指标更新
    for label, ind_code in indicators.items():
        try:
            url = (f"https://api.worldbank.org/v2/country/{codes_param}/indicator/{ind_code}"
                   f"?format=json&per_page=200&date={selected_year}:{selected_year}")
            res = requests.get(url, verify=False, timeout=10)
            if res.status_code == 200:
                payload = res.json()
                records = payload[1] if len(payload) > 1 and payload[1] else []
                if not records:
                    continue
                df_temp = pd.DataFrame(records).dropna(subset=['value'])
                rev_iso = {v: k for k, v in iso_mapping.items()}
                for _, row in df_temp.iterrows():
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


@st.cache_data(ttl=86400, show_spinner=False)
def translate_to_english(text):
    """使用 Google Translate 公共端点将动态新闻文本统一翻译为英文。"""
    if not text or not text.strip():
        return ""
    try:
        response = requests.get(
            "https://translate.googleapis.com/translate_a/single",
            params={"client": "gtx", "sl": "auto", "tl": "en", "dt": "t", "q": text[:4500]},
            headers={"User-Agent": "Mozilla/5.0"},
            timeout=12
        )
        response.raise_for_status()
        payload = response.json()
        translated = "".join(part[0] for part in payload[0] if part and part[0])
        return translated.strip() or "[English translation unavailable]"
    except Exception:
        return "[English translation unavailable]"


def add_english_translations(news_items):
    """为新闻列表补充英文标题和英文摘要，原始链接及源文本保持不变。"""
    translated_items = []
    for item in news_items:
        translated_item = item.copy()
        translated_item["title_en"] = translate_to_english(item.get("title", ""))
        translated_item["desc_en"] = translate_to_english(item.get("desc", ""))
        translated_items.append(translated_item)
    return translated_items


NEWS_TIME_RANGES = {
    "近1个月资讯": 30,
    "近3个月资讯": 90,
    "近半年资讯": 183,
    "近一年资讯": 365,
    "一年以上资讯": None
}


def parse_news_date(date_text):
    """兼容 RSS、Atom 与 ISO 8601 日期，统一返回 UTC 时间。"""
    if not date_text or date_text == "N/A":
        return None
    try:
        parsed = parsedate_to_datetime(date_text)
    except (TypeError, ValueError):
        try:
            parsed = datetime.fromisoformat(date_text.replace("Z", "+00:00"))
        except (TypeError, ValueError):
            return None
    if parsed.tzinfo is None:
        parsed = parsed.replace(tzinfo=timezone.utc)
    return parsed.astimezone(timezone.utc)


def build_historical_feed_url(source, time_range_label):
    """生成限定原媒体域名及时间范围的 Google News RSS 查询。"""
    now = datetime.now(timezone.utc)
    domain = urlparse(source["source_url"]).netloc.lower().removeprefix("www.")
    days = NEWS_TIME_RANGES[time_range_label]
    if days is None:
        date_query = f"before:{(now - timedelta(days=365)).date().isoformat()}"
    else:
        start_date = (now - timedelta(days=days)).date().isoformat()
        end_date = (now + timedelta(days=1)).date().isoformat()
        date_query = f"after:{start_date} before:{end_date}"
    query = quote_plus(f"site:{domain} {date_query} economy OR business OR finance")
    return f"https://news.google.com/rss/search?q={query}&hl=en-US&gl=US&ceid=US:en"


def news_date_matches(published_at, time_range_label):
    if published_at is None:
        return False
    age = datetime.now(timezone.utc) - published_at
    days = NEWS_TIME_RANGES[time_range_label]
    return age.days > 365 if days is None else timedelta(0) <= age <= timedelta(days=days + 1)


@st.cache_data(ttl=1800, show_spinner=False)
def fetch_global_news(country_key, time_range_label):
    config = COUNTRY_CONFIGS.get(country_key)
    sources = NEWS_SOURCES.get(country_key, [])
    if not config or not sources:
        return [], "未找到该国家的新闻源配置。", None

    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/131 Safari/537.36",
        "Accept": "application/rss+xml, application/atom+xml, application/xml, text/xml;q=0.9, */*;q=0.7"
    }
    failures = []

    def node_text(node, names, default=""):
        for child in list(node):
            local_name = child.tag.rsplit('}', 1)[-1].lower()
            if local_name in names and child.text:
                return child.text.strip()
        return default

    for source_index, source in enumerate(sources):
        request_candidates = [
            (build_historical_feed_url(source, time_range_label), True),
            (source["url"], False)
        ]
        for request_url, is_historical_query in request_candidates:
            try:
                response = requests.get(request_url, headers=headers, verify=False, timeout=12)
                response.raise_for_status()
                if not response.content.strip():
                    raise ValueError("返回内容为空")

                root = ET.fromstring(response.content)
                entries = [node for node in root.iter()
                           if node.tag.rsplit('}', 1)[-1].lower() in {"item", "entry"}]
                source_news = []
                seen_links = set()

                for item in entries:
                    title = node_text(item, {"title"}, "No Title")
                    link = node_text(item, {"link"}, "")
                    if not link:
                        for child in list(item):
                            if child.tag.rsplit('}', 1)[-1].lower() == "link":
                                link = child.attrib.get("href", "")
                                if link:
                                    break
                    link = link or source["source_url"]
                    pub_date = node_text(item, {"pubdate", "published", "updated", "date"}, "N/A")
                    published_at = parse_news_date(pub_date)
                    if not news_date_matches(published_at, time_range_label):
                        continue
                    description = node_text(item, {"description", "summary", "content", "encoded"}, "")
                    clean_desc = re.sub(r'\s+', ' ', re.sub('<[^<]+?>', '', description)).strip()

                    if title == "No Title" or link in seen_links:
                        continue
                    seen_links.add(link)
                    label, advice, bg_color, text_color = analyze_global_sentiment(
                        title + " " + clean_desc, country_key)
                    source_news.append({
                        "title": title, "link": link, "date": pub_date, "desc": clean_desc,
                        "sentiment": label, "advice": advice, "bg": bg_color, "tc": text_color,
                        "source": source["name"]
                    })
                    if len(source_news) >= 12:
                        break

                if source_news:
                    source_news.sort(key=lambda item: parse_news_date(item["date"]) or datetime.min.replace(tzinfo=timezone.utc),
                                     reverse=True)
                    active_source = {
                        "name": source["name"], "url": source["source_url"],
                        "is_fallback": source_index > 0,
                        "historical_query": is_historical_query
                    }
                    return source_news, None, active_source
            except Exception as exc:
                failures.append(f"{source['name']}：{str(exc)[:100]}")
        failures.append(f"{source['name']}：所选时间范围内无有效资讯")

    return [], "；".join(failures), None


# ==================== 📡 侧边栏动态过滤与安全防御 ====================
with st.sidebar:
    st.header("🎯 核心系统控制台")
    st.radio(
        "选择你要查看的战略情报模块：",
        options=["📰 模块一：全球实时经济新闻与情绪雷达", "📊 模块二：世界银行大盘与宏微观指标层"],
        key="app_mode"
    )
    if st.session_state["app_mode"] == "📊 模块二：世界银行大盘与宏微观指标层":
        macro_year_options = list(range(datetime.now().year, 1999, -1))
        older_col, newer_col = st.columns(2)
        with older_col:
            if st.button("◀ 上一年", use_container_width=True):
                st.session_state["selected_macro_year"] = max(
                    2000, st.session_state["selected_macro_year"] - 1)
        with newer_col:
            if st.button("下一年 ▶", use_container_width=True):
                st.session_state["selected_macro_year"] = min(
                    datetime.now().year, st.session_state["selected_macro_year"] + 1)
        st.selectbox(
            "📅 选择宏观数据年份",
            options=macro_year_options,
            key="selected_macro_year",
            help="世界银行数据通常存在发布延迟；尚未发布的年度将显示暂无数据。"
        )
        if st.button("🔄 更新所选年份指标", type="primary", use_container_width=True):
            load_real_global_data.clear()
            st.session_state["macro_last_updated"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        st.caption(f"最近手动更新时间：{st.session_state['macro_last_updated'] or '尚未手动更新'}")
    st.markdown("---")
    st.subheader("🔍 维度筛选器")

    df_countries = load_real_global_data(st.session_state["selected_macro_year"])

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

    range_col, refresh_col, status_col = st.columns([2, 1, 3])
    with range_col:
        selected_news_range = st.selectbox(
            "🗓️ 资讯时间范围",
            options=list(NEWS_TIME_RANGES.keys()),
            index=0,
            key="selected_news_range"
        )
    with refresh_col:
        st.write("")
        refresh_news = st.button("🔄 更新最新资讯", type="primary", use_container_width=True)
    if refresh_news:
        fetch_global_news.clear()

    with st.spinner(f"正在抓取并翻译 {st.session_state['selected_country']} · {selected_news_range}..."):
        current_news, news_error, active_source = fetch_global_news(
            st.session_state["selected_country"], selected_news_range)
        if current_news:
            current_news = add_english_translations(current_news)

    if refresh_news and not news_error:
        st.session_state["news_last_updated"][st.session_state["selected_country"]] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    last_updated = st.session_state["news_last_updated"].get(st.session_state["selected_country"])
    with status_col:
        st.caption(f"最近手动更新时间：{last_updated or '尚未手动更新'}")

    if active_source:
        source_state = "备用来源已自动接管" if active_source["is_fallback"] else "主来源运行正常"
        retrieval_mode = "历史资讯检索" if active_source.get("historical_query") else "媒体 RSS"
        st.success(f"📡 当前来源：[{active_source['name']}]({active_source['url']}) · {source_state} · {retrieval_mode}")

    if news_error:
        st.error(news_error)
        st.info("主来源和备用来源均未返回有效资讯，当前不会使用模拟数据。请稍后点击“更新最新资讯”重试。")

    if current_news:
        sentiments = [n['sentiment'] for n in current_news]
        pos_count = sentiments.count("😊 正面 (Positive)")
        neg_count = sentiments.count("😟 负面 (Negative)")
        neu_count = sentiments.count("😐 中性 (Neutral)")
        total = len(current_news)
        sentiment_index = round(((pos_count * 100 + neu_count * 50) / total), 1) if total > 0 else 50

        s_col1, s_col2, s_col3 = st.columns(3)
        s_col1.metric(selected_news_range, f"{total} 条")
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
        st.markdown("### 📢 Live Intelligence Feed (English)")
        for idx, news in enumerate(current_news):
            with st.container():
                st.markdown(f"**[{idx + 1}] [{news['date']}] [{news['title_en']}]({news['link']})**")
                if news['desc_en']: st.caption(f"📝 *Summary:* {news['desc_en']}")
                st.write(
                    f'<div style="background-color:{news["bg"]}; color:{news["tc"]}; padding:8px 12px; border-radius:5px; font-size:14px; margin-bottom:15px;">AI 情绪：{news["sentiment"]} | 💡 建议：{news["advice"]}</div>',
                    unsafe_allow_html=True)

elif st.session_state["app_mode"] == "📊 模块二：世界银行大盘与宏微观指标层":
    selected_macro_year = st.session_state["selected_macro_year"]
    st.subheader(f"📍 {st.session_state['selected_country']} · {selected_macro_year} 年官方宏观经济大盘")
    st.caption("人口、人均 GDP 与老龄化率来自所选年份的世界银行接口；可支配收入和终端渗透率为当前参考指标。")

    kpi1, kpi2, kpi3, kpi4 = st.columns(4)
    kpi1.metric(f"{selected_macro_year} 总人口", format_number(current_country_data['总人口'], 0, suffix=" 人"))
    kpi2.metric(f"{selected_macro_year} 人均 GDP", format_number(current_country_data['人均GDP($)'], 0, prefix="$"))
    kpi3.metric("参考人均可支配收入", format_number(current_country_data['人均可支配收入($)'], 0, prefix="$"))
    kpi4.metric("参考平板PC渗透率", format_number(current_country_data['平板PC产品渗透率(%)'], 1, suffix="%"))

    col1, col2 = st.columns([1, 2])
    with col1:
        st.subheader("📋 宏观结构与社会档案")
        info_df = pd.DataFrame({
            "核心维度": ["大洲板块", "细分区域", "行政首都", "主要语言", "老龄化率"],
            "详情": [current_country_data["所属大洲"], current_country_data["细分区域"], current_country_data["首都"],
                     current_country_data["官方语言"], format_number(current_country_data['人口老龄化率(%)'], 1, suffix="%")]
        })
        st.write(info_df.to_html(index=False, classes='table table-striped'), unsafe_allow_html=True)

    with col2:
        st.subheader("📊 区域大盘终端渗透率对比")
        peer_df = df_countries[df_countries["所属大洲"] == current_country_data["所属大洲"]]
        fig_bar = px.bar(peer_df, x="国家/地区", y="平板PC产品渗透率(%)",
                         title=f"{current_country_data['所属大洲']} 主要国家大盘渗透对比", color="平板PC产品渗透率(%)",
                         color_continuous_scale="Purples")
        style_chart(fig_bar, height=430)
    st.plotly_chart(fig_bar, use_container_width=True)

    st.markdown("---")
    st.subheader("📊 全球宏观指标国家对比")
    chart_metric = st.selectbox("🎯 切换柱状图指标：",
                                ["总人口", "人均GDP($)", "人均可支配收入($)", "平板PC产品渗透率(%)"])
    chart_df = df_countries.dropna(subset=[chart_metric]).sort_values(chart_metric, ascending=True).copy()
    if chart_df.empty:
        st.warning(f"世界银行尚未提供 {selected_macro_year} 年的【{chart_metric}】数据，请选择更早年份。")
    else:
        fig_global_bar = px.bar(
            chart_df,
            x=chart_metric,
            y="国家/地区",
            color="所属大洲",
            orientation="h",
            text_auto=".3s",
            title=f"{selected_macro_year} 年各国【{chart_metric}】具体数值与区域对比",
            hover_data={"三字代码(ISO)": True, "细分区域": True, chart_metric: ":,.2f"},
            color_discrete_sequence=["#22d3ee", "#4f7cff", "#8b5cf6", "#34d399", "#f59e0b"]
        )
        fig_global_bar.update_traces(textposition="outside", cliponaxis=False)
        fig_global_bar.update_layout(
            barmode="group",
            legend_title_text="战略区域",
            xaxis_title=chart_metric,
            yaxis_title="",
            bargap=0.28
        )
        style_chart(fig_global_bar, height=760)
        st.plotly_chart(fig_global_bar, use_container_width=True)

st.markdown("---")
if st.checkbox("🔍 显示全量清洗后的底层 Dataframe 明细"):
    st.dataframe(df_countries, use_container_width=True)
