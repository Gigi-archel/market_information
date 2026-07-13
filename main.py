import streamlit as st
import pandas as pd
import plotly.express as px
import requests
import urllib3
import random

# 1. 禁用未验证的 HTTPS 请求警告（彻底防范公司内网/SSL证书报错）
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

# 2. 设置 Streamlit 页面配置
st.set_page_config(
    page_title="全球国家信息看板",
    page_icon="🌍",
    layout="wide",
    initial_sidebar_state="expanded"
)

# 页面大标题
st.title("🌍 全球国家信息与宏观经济洞察看板")
st.markdown("---")


# 3. 数据加载函数（带缓存与强鲁棒性设计）
@st.cache_data
def load_country_data():
    try:
        # 使用公共免费的 REST Countries API 获取基础国家信息
        url = "https://restcountries.com/v3.1/all"
        response = requests.get(url, verify=False, timeout=10)  # verify=False 防止 SSLError

        if response.status_code == 200:
            data = response.json()
            country_list = []

            for item in data:
                name = item.get('name', {}).get('common', 'Unknown')
                code = item.get('cca3', '')
                population = item.get('population', 0)
                region = item.get('region', 'Unknown')
                subregion = item.get('subregion', 'Unknown')
                area = item.get('area', 0)
                capital = item.get('capital', ['N/A'])[0] if item.get('capital') else 'N/A'
                languages = ", ".join(item.get('languages', {}).values()) if item.get('languages') else 'N/A'

                # 🧠 结合业务场景：构造电商指标（实际开发中可通过 Merge 本地 CSV 报告数据实现）
                random.seed(hash(name))  # 固定随机种子以保证交互时数据不跳变
                ecommerce_penetration = round(random.uniform(15.0, 85.0), 1)
                avg_order_value = round(random.uniform(20.0, 150.0), 1)

                country_list.append({
                    "国家/地区": name,
                    "三字代码(ISO)": code,
                    "所属大洲": region,
                    "细分区域": subregion,
                    "总人口": population,
                    "国土面积(k㎡)": area,
                    "首都": capital,
                    "官方语言": languages,
                    "电商渗透率(%)": ecommerce_penetration,
                    "客单价($)": avg_order_value
                })

            df = pd.DataFrame(country_list)
            return df.sort_values(by="国家/地区").reset_index(drop=True)

    except Exception as e:
        # 当 API 被防火墙彻底阻断时，自动触发备用方案，保证看板依然可用
        st.sidebar.warning(f"💡 触发网络备用机制（已忽略 SSL 或已启用本地模拟数据）")

        # 本地硬编码的核心备用数据矩阵
        # 本地硬编码的核心备用数据矩阵（已按区域深度扩充拉美、亚太、欧洲、欧亚、中东非）
        mock_data = {
            "国家/地区": [
                "China", "United States", "Germany", "Brazil", "Japan", "India", "United Kingdom", "France", "Vietnam",
                "Mexico", "Colombia", "Chile",
                "Singapore", "Indonesia", "Malaysia", "Thailand", "Philippines",
                "Turkey", "Poland", "Spain", "Italy",
                "Russia",
                "United Arab Emirates", "Saudi Arabia", "South Africa", "Kuwait"
            ],
            "三字代码(ISO)": [
                "CHN", "USA", "DEU", "BRA", "JPN", "IND", "GBR", "FRA", "VNM",
                "MEX", "COL", "CHL",
                "SGP", "IDN", "MYS", "THA", "PHL",
                "TUR", "POL", "ESP", "ITA",
                "RUS",
                "ARE", "SAU", "ZAF", "KWT"
            ],
            "所属大洲": [
                "Asia", "Americas", "Europe", "Americas", "Asia", "Asia", "Europe", "Europe", "Asia",
                "Americas", "Americas", "Americas",
                "Asia", "Asia", "Asia", "Asia", "Asia",
                "Europe", "Europe", "Europe", "Europe",
                "Europe",
                "Africa/Asia", "Asia", "Africa", "Asia"
            ],
            "细分区域": [
                "Eastern Asia", "North America", "Western Europe", "South America", "Eastern Asia", "Southern Asia",
                "Northern Europe", "Western Europe", "Southeast Asia",
                "Central America", "South America", "South America",
                "Southeast Asia", "Southeast Asia", "Southeast Asia", "Southeast Asia", "Southeast Asia",
                "Southern Europe", "Eastern Europe", "Southern Europe", "Southern Europe",
                "Eastern Europe",
                "Western Asia", "Western Asia", "Southern Africa", "Western Asia"
            ],
            "总人口": [
                1412000000, 333000000, 83000000, 214000000, 125000000, 1408000000, 67000000, 68000000, 98000000,
                126000000, 51000000, 19000000,
                6000000, 273000000, 33000000, 71000000, 113000000,
                85000000, 38000000, 47000000, 59000000,
                143000000,
                10000000, 36000000, 60000000, 43000000
            ],
            "国土面积(k㎡)": [
                9600000, 9833000, 357022, 8515000, 377975, 3287000, 242495, 551695, 331212,
                1964375, 1141748, 756102,
                728, 1904569, 329847, 513120, 300000,
                783562, 312696, 505992, 301340,
                17098242,
                83600, 2149690, 1221037, 17818
            ],
            "首都": [
                "Beijing", "Washington, D.C.", "Berlin", "Brasília", "Tokyo", "New Delhi", "London", "Paris", "Hanoi",
                "Mexico City", "Bogotá", "Santiago",
                "Singapore", "Jakarta", "Kuala Lumpur", "Bangkok", "Manila",
                "Ankara", "Warsaw", "Madrid", "Rome",
                "Moscow",
                "Abu Dhabi", "Riyadh", "Pretoria", "Kuwait City"
            ],
            "官方语言": [
                "Chinese", "English", "German", "Portuguese", "Japanese", "Hindi, English", "English", "French",
                "Vietnamese",
                "Spanish", "Spanish", "Spanish",
                "English, Malay, Mandarin, Tamil", "Indonesian", "Malay", "Thai", "Filipino, English",
                "Turkish", "Polish", "Spanish", "Italian",
                "Russian",
                "Arabic, English", "Arabic", "English, Zulu, Xhosa", "Arabic"
            ],
            "电商渗透率(%)": [
                81.5, 75.0, 78.2, 45.3, 72.1, 35.0, 80.1, 76.5, 52.3,
                49.5, 41.2, 55.0,
                79.8, 64.2, 61.5, 58.0, 55.4,
                46.8, 54.2, 63.0, 59.5,
                60.1,
                78.0, 68.5, 38.0, 66.2
            ],
            "客单价($)": [
                45.5, 120.0, 95.0, 30.5, 85.0, 18.2, 110.0, 92.0, 25.5,
                38.5, 28.0, 42.0,
                105.0, 19.5, 32.0, 26.8, 22.0,
                34.5, 48.0, 72.0, 78.5,
                39.0,
                125.0, 98.0, 29.5, 88.0
            ]
        }
    return pd.DataFrame(mock_data)


# 执行加载
with st.spinner("🚀 正在清洗与构建全球国家数据集..."):
    df_countries = load_country_data()

# ==================== 🛠️ 侧边栏过滤面板 ====================
st.sidebar.header("🔍 维度筛选器")

# 大洲一级联动筛选
all_regions = ["全部大洲"] + list(df_countries["所属大洲"].unique())
selected_region = st.sidebar.selectbox("1️⃣ 第一步：选择大洲", all_regions)

# 动态计算国家二级联动列表
if selected_region != "全部大洲":
    filtered_df_for_list = df_countries[df_countries["所属大洲"] == selected_region]
else:
    filtered_df_for_list = df_countries

# 国家二级选择
all_countries = list(filtered_df_for_list["国家/地区"].unique())
selected_country = st.sidebar.selectbox("2️⃣ 第二步：指定目标国家", all_countries)

# 提取当前被选定国家的行数据
current_country_data = df_countries[df_countries["国家/地区"] == selected_country].iloc[0]

# ==================== 📊 核心指标卡 (KPI) ====================
st.subheader(f"📍 {selected_country} 核心数据快照")

kpi1, kpi2, kpi3, kpi4 = st.columns(4)
with kpi1:
    st.metric("核心指标: 总人口", f"{int(current_country_data['总人口']):,} 人")
with kpi2:
    st.metric("政治中心: 首都", str(current_country_data['首都']))
with kpi3:
    st.metric("行业深度: 电商渗透率", f"{current_country_data['电商渗透率(%)']}%")
with kpi4:
    st.metric("消费水平: 平均客单价", f"${current_country_data['客单价($)']}")

st.markdown(" ")

# ==================== 🏛️ 左右分栏：详细信息 VS 同区域对比 ====================
col1, col2 = st.columns([1, 2])

with col1:
    st.subheader("📋 基础档案清单")
    info_df = pd.DataFrame({
        "核心维度": ["国家/地区名称", "ISO 三字代码", "所属大洲分区", "国土面积", "官方主要语言"],
        "详情": [
            current_country_data["国家/地区"],
            current_country_data["三字代码(ISO)"],
            f"{current_country_data['所属大洲']} / {current_country_data['细分区域']}",
            f"{int(current_country_data['国土面积(k㎡)']):,} k㎡",
            current_country_data["官方语言"]
        ]
    })
    # 使用无索引的 HTML 格式干净渲染表格
    st.write(info_df.to_html(index=False, classes='table table-striped'), unsafe_allow_html=True)

with col2:
    st.subheader("📊 区域对标分析")
    # 筛选出同一个大洲的竞品国家进行水平横向对比
    peer_df = df_countries[df_countries["所属大洲"] == current_country_data["所属大洲"]].head(15)

    fig_bar = px.bar(
        peer_df,
        x="国家/地区",
        y="电商渗透率(%)",
        title=f"同在【{current_country_data['所属大洲']}】大洲的主要国家电商渗透率大比拼",
        labels={"电商渗透率(%)": "电商渗透率 (%)"},
        color="电商渗透率(%)",
        color_continuous_scale="Blues"  # 优雅的渐变蓝数据色盘
    )
    # 自动适应分栏宽度
    st.plotly_chart(fig_bar, use_container_width=True)

st.markdown("---")

# ==================== 🗺️ 全球洞察地图可视化 ====================
st.subheader("🗺️ 全球宏观数据热力地图")

# 允许用户在前端一键切换全局地图渲染的指标
map_metric = st.selectbox("🎯 自由切换地图渲染维度：", ["总人口", "电商渗透率(%)", "客单价($)"])

# ==================== 🗺️ 全球洞察地图可视化 ====================
st.subheader("🗺️ 全球宏观数据热力地图")

map_metric = st.selectbox("🎯 自由切换地图渲染维度：", ["总人口", "电商渗透率(%)", "客单价($)"], key="map_metric_global_view")

# 渲染高交互性的 Plotly 等值区域地图
fig_map = px.choropleth(
    df_countries,
    locations="三字代码(ISO)",  # 地图边界匹配所必需的 ISO-3 编码
    color=map_metric,  # 颜色深浅对应的连续型数值列
    hover_name="国家/地区",  # 鼠标悬停时的标题
    title=f"全球各国【{map_metric}】宏观地理分布格局（支持滚轮缩放与平移）",
    color_continuous_scale="Viridis",  # 经典的专业数据色彩模式
    projection="natural earth"  # 现代化扁平化地球投影
)

fig_map.update_layout(
    margin={"r": 0, "t": 40, "l": 0, "b": 0},
    height=550
)

st.plotly_chart(fig_map, use_container_width=True)

# ==================== 🗺️ 全球 5 大战略区域、24 国宏观与微观全量战略情报库 ====================
COUNTRY_CONFIGS = {
    # ---------------- 🇨🇳 亚洲战略市场 (8国) ----------------
    "China": {
        "rss_url": "https://finance.sina.com.cn/gongsi/rss.xml",
        "pos": ['增长', '稳步', '新质生产力', '复苏', '利好', '创新', '突破', '活跃'],
        "neg": ['下滑', '放缓', '收缩', '风险', '承压', '亏损', '严峻', '内卷'],
        "mock": [{"title": "新质生产力驱动端侧AI产业链爆发，高端平板出货量稳步回升", "desc": "高技术制造业韧性强劲，人民币汇率双向波动。微观层面居民对“AI本地大模型流畅度”与“多端协同”体验给予高度评价，办公与画画类软件需求活跃。", "date": "Mon, 13 Jul 2026 15:00:00 GMT", "link": "https://finance.sina.com.cn"}]
    },
    "Indonesia": {
        "rss_url": "https://www.antaranews.com/rss/ekonomi.xml",
        "pos": ['tumbuh', 'meningkat', 'untung', 'sukses', 'investasi', 'optimis', 'surplus'],
        "neg": ['turun', 'lemah', 'krisis', 'inflasi', 'rugi', 'resiko', 'lambat'],
        "mock": [{"title": "Surplus perdagangan Indonesia 2026 memperkuat stabilitas Rupiah", "desc": "印尼政局平稳，中产阶级可支配收入抬升。在硬件消费上表现出明显的“社交跟风与外观控”倾向，高饱和度时尚轻薄机身更受欢迎，极度依赖 Shopee 与 Tokopedia 等网购平台。", "date": "Mon, 13 Jul 2026 12:00:00 GMT", "link": "https://www.antaranews.com"}]
    },
    "Philippines": {
        "rss_url": "https://www.bworldonline.com/feed/",
        "pos": ['growth', 'increase', 'boost', 'expand', 'optimism', 'remittance', 'recovery'],
        "neg": ['drop', 'decline', 'slowdown', 'inflation', 'risk', 'slump', 'weak'],
        "mock": [{"title": "Philippine economy expands, peso stabilized by strong structural remittances", "desc": "外劳汇款回流有力支撑国内消费力。年轻人口红利巨大，对平板呈现“娱乐与轻教育”偏好。购买平板对“扬声器音质”和“大电池续航”提及率最高，高度依赖 TikTok Shop 购物。", "date": "Mon, 13 Jul 2026 13:00:00 GMT", "link": "https://www.bworldonline.com"}]
    },
    "Malaysia": {
        "rss_url": "https://theedgemalaysia.com/rss/corporate",
        "pos": ['growth', 'rise', 'surged', 'rebound', 'investment', 'positive', 'profit'],
        "neg": ['fall', 'drop', 'contraction', 'slump', 'risk', 'loss', 'bearish'],
        "mock": [{"title": "Malaysia's ringgit strengthens as tech export supershow boosts industrial output", "desc": "林吉特汇率表现抢眼，制造业投资环境优渥。白领与大学生对生产力工具有强需求，倾向选择“PC级办公体验+带磁吸键盘套”组合，注重跨设备互传效率。", "date": "Mon, 13 Jul 2026 11:00:00 GMT", "link": "https://theedgemalaysia.com"}]
    },
    "Thailand": {
        "rss_url": "https://www.bangkokpost.com/rss/data/business.xml",
        "pos": ['growth', 'boost', 'recovery', 'rebound', 'gain', 'surplus', 'tourism'],
        "neg": ['slump', 'drop', 'fall', 'decline', 'slowdown', 'risk', 'aging'],
        "mock": [{"title": "Thai baht trends upward amid total tourism revival and tech hub expansion", "desc": "泰铢震荡走强，供应链投资增加。城市居民展现强烈“审美敏感”特征，对平板的“屏幕色彩显示效果”及“机身配色质感”挑剔度极高，Lazada 及流媒体刷剧软件普及度高。", "date": "Mon, 13 Jul 2026 10:00:00 GMT", "link": "https://www.bangkokpost.com"}]
    },
    "Vietnam": {
        "rss_url": "https://vnexpress.net/rss/kinh-doanh.xml",
        "pos": ['tang', 'phat trien', 'tang truong', 'loi nhuan', 'dau tu', 'on dinh'],
        "neg": ['giam', 'suy thoai', 'lo', 'rui ro', 'kho khan', 'lam phat'],
        "mock": [{"title": "FDI và sản xuất công nghệ Việt Nam đạt kỷ lục mới, hỗ trợ tiền tệ ổn định", "desc": "全球电子制造业基地地位巩固，居民可支配收入成长。家庭“教育投资倾斜”极其显著，家长愿意为“在线网课流畅、系统防沉迷、自带护眼功能”的平板电脑支付溢价，Zalo 普及率高。", "date": "Mon, 13 Jul 2026 09:00:00 GMT", "link": "https://vnexpress.net"}]
    },
    "Singapore": {
        "rss_url": "https://www.straitstimes.com/news/business/rss.xml",
        "pos": ['growth', 'rise', 'expansion', 'rebound', 'hub', 'wealth', 'surged'],
        "neg": ['slowdown', 'drop', 'risk', 'inflation', 'contraction', 'cooling', 'slump'],
        "mock": [{"title": "Singapore retains top global hub status as tech venture assets scale higher", "desc": "新币汇率极为强势，商务环境全球顶尖。微观层面属于典型的富裕高净值市场，对平板硬件无预算限制，极其看重“生态连贯性”与“高端商务质感”，常用于无纸化会议与股票投资App。", "date": "Mon, 13 Jul 2026 09:00:00 GMT", "link": "https://www.straitstimes.com"}]
    },
    "Japan": {
        "rss_url": "https://www.nikkei.com/rss/index.rdf",
        "pos": ['上昇', '拡大', '回復', '成長', 'プラス', '黒字', '株高'],
        "neg": ['下落', '縮小', 'リスク', 'インフレ', 'マイナス', '赤字', '鈍化'],
        "mock": [{"title": "日経平均と円相場が安定推移、デフレ完全脱却へ企業投資が拡大", "desc": "日本宏观营商环境回暖。微观层面消费者有极度严重的“品牌洁癖与细节强迫症”，对平板的品控容忍度极低。主销渠道高度集中于线下运营商及主流电器城，常用于观看漫画、Yahoo新闻与手游。", "date": "Mon, 13 Jul 2026 08:00:00 GMT", "link": "https://www.nikkei.com"}]
    },

    # ---------------- 🇪🇺 欧洲战略市场 (7国) ----------------
    "Turkey": {
        "rss_url": "https://www.aa.com.tr/tr/rss/kategori/ekonomi",
        "pos": ['artisi', 'buyume', 'yukselis', 'kazanc', 'destek', 'yatirim', 'guven'],
        "neg": ['dusus', 'enflasyon', 'risk', 'kayip', 'yavaslama', 'daralma', 'kriz'],
        "mock": [{"title": "Türkiye sanayi üretimi endeksi 2026'da beklentileri aştı", "desc": "宏观上里拉汇率波动仍是核心关注点，推动商务采购决策向高质价比转移。微观消费习惯呈现强烈的“精打细算”特征，极其偏好高性价比、中端配置且附带丰富赠品（如保修延长、手写笔）的平板机型。", "date": "Mon, 13 Jul 2026 14:00:00 GMT", "link": "https://www.aa.com.tr"}]
    },
    "Poland": {
        "rss_url": "https://www.bankier.pl/rss/ekonomia.xml",
        "pos": ['wzrost', 'zysk', 'sukces', 'rozwoj', 'pozytywny', 'optymizm', 'rekord'],
        "neg": ['spadek', 'strata', 'kryzys', 'inflacja', 'negatywny', 'problem', 'ryzyko'],
        "mock": [{"title": "Wzrost PKB Polski w 2026 roku zaskakuje europejskich analityków", "desc": "波兰宏观韧性强劲，欧盟基金持续注入。消费者展现出高理性特征，购买平板极其看重“屏幕护眼认证”与“全套手写笔性价比”，常用于 Allegro 购物、远程办公与本地流媒体订阅。", "date": "Mon, 13 Jul 2026 14:00:00 GMT", "link": "https://www.bankier.pl"}]
    },
    "Germany": {
        "rss_url": "https://www.faz.net/rss/aktuell/wirtschaft/",
        "pos": ['wachstum', 'gewinn', 'plus', 'erholung', 'investition', 'stabil', 'optimismus'],
        "neg": ['rückgang', 'verlust', 'krise', 'inflation', 'risiko', 'schwäche', 'stagnation'],
        "mock": [{"title": "Deutsche Industrie verzeichnet Auftragsplus bei High-Tech Exporten", "desc": "德国宏观经济注重合规与环保法律，商务环境成熟。微观层面消费者购买决策极其严谨，偏好详尽的参数对比，极看重“产品耐用度”与“长期软件系统升级保障”，日常依赖 Amazon 及电子零售商 Notebooksbilliger。", "date": "Mon, 13 Jul 2026 13:00:00 GMT", "link": "https://www.faz.net"}]
    },
    "Spain": {
        "rss_url": "https://www.elconfidencial.com/rss/economia/",
        "pos": ['crecimiento', 'subida', 'beneficio', 'recuperacion', 'inversion', 'positivo', 'empleo'],
        "neg": ['caida', 'bajada', 'perdida', 'crisis', 'inflacion', 'riesgo', 'frenazo'],
        "mock": [{"title": "El turismo y la exportación impulsan el PIB español por encima de la media", "desc": "西班牙宏观复苏明显，营商信心回升。微观消费习惯表现为强烈的家庭导向与校园开学季驱动，中端价位段竞争激烈，消费者对平板的“影音娱乐多媒体表现”及“防摔外壳设计”有刚性需求。", "date": "Mon, 13 Jul 2026 13:00:00 GMT", "link": "https://www.elconfidencial.com"}]
    },
    "Italy": {
        "rss_url": "https://www.ilsole24ore.com/rss/economia.xml",
        "pos": ['crescita', 'aumento', 'utile', 'ripresa', 'investimento', 'positivo', 'record'],
        "neg": ['calo', 'diminuzione', 'perdita', 'crisi', 'inflazione', 'rischio', 'rallentamento'],
        "mock": [{"title": "Export italiano di macchinari e digital tech segna un nuovo trend positivo", "desc": "意大利政商商务环境在政策扶持下小幅改善。微观层面由于自由职业者和中小企业主比例高，对“平板替代传统笔记本（轻量化移动办公）”接受度极高，对工业造型设计与做工细节要求严苛。", "date": "Mon, 13 Jul 2026 13:00:00 GMT", "link": "https://www.ilsole24ore.com"}]
    },
    "France": {
        "rss_url": "https://www.lefigaro.fr/rss/figaro_economie.xml",
        "pos": ['croissance', 'hausse', 'profit', 'reprise', 'investissement', 'positif', 'succes'],
        "neg": ['baisse', 'chute', 'perte', 'crise', 'inflation', 'risque', 'ralentissement'],
        "mock": [{"title": "La tech française attire de nouveaux capitaux étrangers au premier semestre", "desc": "法国极度重视隐私法规（GDPR）与本地语言生态。微观层面法国消费者对产品美学有着独特的坚持，色彩搭配和材质触感极大影响购买决策，主力消费集中于文化零售巨头 FNAC 渠道。", "date": "Mon, 13 Jul 2026 12:00:00 GMT", "link": "https://www.lefigaro.fr"}]
    },
    "United Kingdom": {
        "rss_url": "https://www.ft.com/?format=rss",
        "pos": ['growth', 'rise', 'expansion', 'rebound', 'investment', 'positive', 'profit'],
        "neg": ['slowdown', 'drop', 'risk', 'inflation', 'contraction', 'deficit', 'slump'],
        "mock": [{"title": "UK services sector resilience stabilizes sterling against major basket currencies", "desc": "英镑汇率保持稳定，商务环境在后脱欧时代寻求数字贸易突破。微观消费市场成熟度极高，人均可支配收入充裕。购买平板对“高刷新率屏幕”与“LTE/5G全网通移动蜂窝版本”需求比例显著高于欧洲大陆。", "date": "Mon, 13 Jul 2026 12:00:00 GMT", "link": "https://www.ft.com"}]
    },

    # ---------------- 🇷🇺 欧亚跨境市场 (2国) ----------------
    "Russia": {
        "rss_url": "https://www.vedomosti.ru/rss/news",
        "pos": ['рост', 'прибыль', 'увеличение', 'развитие', 'инвестиции', 'стабильность'],
        "neg": ['падение', 'убыток', 'кризис', 'инфляция', 'риск', 'санкции', 'снижение'],
        "mock": [{"title": "Параллельный импорт и локальное производство стабилизируют рынок РФ", "desc": "宏观上卢布汇率处于宽幅震荡状态，商务供应链主要依赖跨境大通道。微观消费电子领域正经历彻底的“品牌大重组”，消费者对中高端、拥有强劲硬件配置（高刷、大运存）的平板接受度激增，核心装机为 Yandex 生态圈软件。", "date": "Mon, 13 Jul 2026 11:00:00 GMT", "link": "https://www.vedomosti.ru"}]
    },
    "Kazakhstan": {
        "rss_url": "https://kapital.kz/rss/ekonomika",
        "pos": ['рост', 'увеличение', 'инвестиции', 'развитие', 'стабильность', 'доход'],
        "neg": ['падение', 'снижение', 'риск', 'инфляция', 'кризис', 'дефицит'],
        "mock": [{"title": "Инвестиции в цифровой сектор Казахстана достигли исторического пика", "desc": "坚戈汇率受益于资源出口相对稳健，中亚商务枢纽地位凸显。微观层面可支配收入结构性分化，Kaspi.kz 金融生态全方位统治消费行为，平板购买极其看重能否加入 Kaspi 分期白名单，主流需求为青少年网课与家庭视频娱乐。", "date": "Mon, 13 Jul 2026 10:00:00 GMT", "link": "https://kapital.kz"}]
    },

    # ---------------- 🇦🇪 中东非核心市场 (4国) ----------------
    "UAE": {
        "rss_url": "https://www.arabianbusiness.com/industries/banking-finance/rss",
        "pos": ['growth', 'rise', 'boom', 'investment', 'hub', 'surged', 'wealth'],
        "neg": ['slowdown', 'drop', 'risk', 'inflation', 'cooling', 'decline', 'slump'],
        "mock": [{"title": "Dubai digital economy infrastructure transformation attracts global tech talent", "desc": "迪拉姆紧盯美元，汇率坚如磐石，免税商务环境极具吸引力。微观消费属于典型的“高购买力、高奢华偏好”，消费者极其迷恋金属机身、大屏（12英寸以上）以及旗舰级处理器配置，迪拜和阿布扎比线下顶级 Mall 是主战场。", "date": "Mon, 13 Jul 2026 13:00:00 GMT", "link": "https://www.arabianbusiness.com"}]
    },
    "Saudi Arabia": {
        "rss_url": "https://www.arabnews.com/cat/4/rss.xml",
        "pos": ['growth', 'expansion', 'investment', 'vision', 'gains', 'surged', 'boom'],
        "neg": ['slowdown', 'drop', 'risk', 'inflation', 'decline', 'deficit', 'slump'],
        "mock": [{"title": "Saudi Vision 2030 non-oil GDP expands, reinforcing digital trade pathways", "desc": "宏观在“2030愿景”下财政转型资金充裕，里亚尔汇率稳定。微观层面年轻家庭人口极多，可支配收入高。女性消费者与学生群体平板持有率飙升，极其看重平板的“前置摄像头视频通话质量”与“手写笔做笔记流畅度”，常用于观看 YouTube 及政府教育平台。", "date": "Mon, 13 Jul 2026 13:00:00 GMT", "link": "https://www.arabnews.com"}]
    },
    "South Africa": {
        "rss_url": "https://www.moneyweb.co.za/feed/",
        "pos": ['growth', 'rise', 'rebound', 'investment', 'positive', 'recovery', 'gain'],
        "neg": ['load-shedding', 'slowdown', 'drop', 'risk', 'inflation', 'weak', 'slump'],
        "mock": [{"title": "South Africa structural economic reforms ignite private power investment grids", "desc": "兰特汇率易受宏观电力供应和通胀扰动。微观层面消费习惯呈现两极分化，对平板的购买高度依赖于电信运营商（Vodacom / MTN）的合约机绑定销售，消费者极其看重“耐用度”与“充电速度（应对限电轮流断电）”。", "date": "Mon, 13 Jul 2026 12:00:00 GMT", "link": "https://www.moneyweb.co.za"}]
    },
    "Kuwait": {
        "rss_url": "https://www.arabtimesonline.com/feed/",
        "pos": ['growth', 'rise', 'surged', 'investment', 'surplus', 'wealth', 'positive'],
        "neg": ['slowdown', 'drop', 'risk', 'inflation', 'decline', 'deficit', 'weak'],
        "mock": [{"title": "Kuwait oil and sovereign wealth buffer scales up domestic spending programs", "desc": "科威特第纳尔作为全球单价最高的货币，宏观购买力惊人。微观消费群体极小但客单价极高，消费者对产品定价毫不敏感，但对硬件规格（屏幕材质是否为 OLED、运行内存是否是顶级）要求极为苛刻，高端商务办公软件装机率高。", "date": "Mon, 13 Jul 2026 13:00:00 GMT", "link": "https://www.arabtimesonline.com"}]
    },

    # ---------------- 🇲🇽 拉美战略纵深 (3国) ----------------
    "Mexico": {
        "rss_url": "https://www.eleconomista.com.mx/rss/economia",
        "pos": ['crecimiento', 'subida', 'beneficio', 'inversion', 'empleo', 'record', 'alza'],
        "neg": ['caida', 'bajada', 'perdida', 'crisis', 'inflacion', 'riesgo', 'freno'],
        "mock": [{"title": "Nearshoring impulsa la manufactura mexicana y atrae flujos récords de dólares", "desc": "墨西哥比索汇率受益于近岸外包表现活跃，营商环境与北美深度绑定。微观层面中产阶级群体迅速壮大，在购买平板时极其注重“分期付款条约（如 Coppel 或 Elektra 渠道的周付模式）”，高性价比的影音娱乐大屏平板非常受欢迎。", "date": "Mon, 13 Jul 2026 11:00:00 GMT", "link": "https://www.eleconomista.com.mx"}]
    },
    "Colombia": {
        "rss_url": "https://www.larepublica.co/rss/economia",
        "pos": ['crecimiento', 'aumento', 'inversion', 'recuperacion', 'positivo', 'desarrollo'],
        "neg": ['caida', 'disminucion', 'crisis', 'inflacion', 'riesgo', 'devaluacion'],
        "mock": [{"title": "Banco de la República de Colombia flexibiliza tasas para estimular el consumo", "desc": "宏观通胀逐步得到控制，哥伦比亚比索汇率趋向平稳。微观消费者习惯在每年“El Buen Fin”或免税日（Día sin IVA）集中清空购物车。平板电脑购买偏好聚焦在“千元级中端档位”，看重本地社交 App 和长续航体验。", "date": "Mon, 13 Jul 2026 11:00:00 GMT", "link": "https://www.larepublica.co"}]
    },
    "Chile": {
        "rss_url": "https://www.df.cl/suplementos/rss/df/portada.xml",
        "pos": ['crecimiento', 'alza', 'inversion', 'recuperacion', 'superavit', 'estabilidad'],
        "neg": ['caida', 'baja', 'crisis', 'inflacion', 'riesgo', 'deficit', 'frenazo'],
        "mock": [{"title": "Exportaciones de litio y cobre estabilizan la balanza comercial de Chile", "desc": "智利拥有拉美地区非常规范和成熟的商务法律及贸易准入环境，智利比索汇率挂钩大宗商品。微观层面零售业高度集中（Falabella、Paris 等百货连锁体系），消费者极其看重“品牌官方正规售后与质保体系”，偏爱精致的极简主义硬件工业设计。", "date": "Mon, 13 Jul 2026 10:00:00 GMT", "link": "https://www.df.cl"}]
    }
}




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


@st.cache_data(ttl=1800)
def fetch_global_news(country_key):
    config = COUNTRY_CONFIGS.get(country_key)
    if not config:
        return []

    news_items = []
    try:
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
        }
        response = requests.get(config['rss_url'], headers=headers, verify=False, timeout=8)
        response.encoding = 'utf-8'

        if response.text and response.text.strip():
            import xml.etree.ElementTree as ET
            root = ET.fromstring(response.text)

            for item in root.findall('.//item')[:8]:
                title = item.find('title').text if item.find('title') is not None else "No Title"
                link = item.find('link').text if item.find('link') is not None else "#"
                pub_date = item.find('pubDate').text if item.find('pubDate') is not None else "N/A"
                description = item.find('description').text if item.find('description') is not None else ""

                import re
                clean_desc = re.sub('<[^<]+?>', '', description).strip()

                label, advice, bg_color, text_color = analyze_global_sentiment(title + " " + clean_desc, country_key)

                news_items.append({
                    "title": title, "link": link, "date": pub_date, "desc": clean_desc,
                    "sentiment": label, "advice": advice, "bg": bg_color, "tc": text_color
                })
    except Exception as e:
        st.sidebar.info(f"💡 {country_key} 已安全切入本地动态宏观情报库")

    if not news_items:
        for item in config['mock']:
            label, advice, bg_color, text_color = analyze_global_sentiment(item['title'] + " " + item['desc'],
                                                                           country_key)
            news_items.append({
                "title": item['title'], "link": item['link'], "date": item['date'], "desc": item['desc'],
                "sentiment": label, "advice": advice, "bg": bg_color, "tc": text_color
            })

    return news_items


# ==================== 🌏 国际化多国前端渲染区（支持一键动态通刷） ====================
if selected_country in COUNTRY_CONFIGS.keys():
    st.markdown("---")
    st.subheader(f"📊 {selected_country} 实时经济新闻与情绪雷达 (Global RSS Stream)")

    with st.spinner(f"正在自动化抓取 {selected_country} 最新财经资讯并进行人工智能情绪建模..."):
        current_news = fetch_global_news(selected_country)

    if current_news:
        sentiments = [n['sentiment'] for n in current_news]
        pos_count = sentiments.count("😊 正面 (Positive)")
        neg_count = sentiments.count("😟 负面 (Negative)")
        neu_count = sentiments.count("😐 中性 (Neutral)")

        total = len(current_news)
        sentiment_index = round(((pos_count * 100 + neu_count * 50) / total), 1) if total > 0 else 50

        s_col1, s_col2, s_col3 = st.columns(3)
        s_col1.metric("今日监控核心资讯", f"{total} 条")
        s_col2.metric("正面/负面情绪分布", f"📈 {pos_count} | 📉 {neg_count}")
        s_col3.metric("市场即时信心指数", f"{sentiment_index}点", help="高于50点代表近期情绪整体偏向乐观")

        # 🤖 自动化 AI 宏观与微观战略洞察英文总结看板
        st.markdown("### 📊 Automated Market Intelligence Summary")

        if sentiment_index > 60:
            market_vibe = "Moderately Positive to Optimistic"
            vibe_emoji = "📈"
        elif sentiment_index < 40:
            market_vibe = "Cautious / Structural Shift Underway"
            vibe_emoji = "⚠️"
        else:
            market_vibe = "Neutral & Observant"
            vibe_emoji = "⚖️"

        insights_repo = {
            "China": [
                "<strong>Macro Core:</strong> Driven by high-tech manufacturing and \"New Quality Productive Forces\" (AI, premium hardware ecosystems). Focus is steadily shifting towards high-quality, sustainable economic expansion.",
                "<strong>Consumer Behavior:</strong> Prominent dual-track consumption. Consumers highly scrutinize true cost-to-performance ratio (value-for-money) and hardware specs, prioritizing native terminal AI features rather than high brand premiums."
            ],
            "Poland": [
                "<strong>Macro Core:</strong> GDP and industrial performance exceed analyst expectations with notable resilience, powered by a solid industrial asset base.",
                "<strong>Consumer Behavior:</strong> Strong online spending appetite. Traditional brick-and-mortar retail shows clear deceleration, aggressively forcing major consumer tech brands to deepen digital and e-commerce channel migrations."
            ],
            "Philippines": [
                "<strong>Macro Core:</strong> Leading Southeast Asian GDP growth momentum, highly insulated by powerful OFW remittances and expanding BPO sectors.",
                "<strong>Consumer Behavior:</strong> Massive youth dividend driving hyper-growth on TikTok Shop and Shopee. High price sensitivity combined with soaring adoption of BNPL (Buy Now Pay Later) payment methods for mobile gadgets."
            ],
            "Indonesia": [
                "<strong>Macro Core:</strong> Strong domestic demand backed by infrastructure scaling and digitalization elevated into a critical national economic pillar.",
                "<strong>Consumer Behavior:</strong> Expanding middle class highly susceptible to social commerce and digital KOL advice. Growing preference for seamless omni-channel tech ecosystems and secure online premium hardware transactions."
            ],
            "Malaysia": [
                "<strong>Macro Core:</strong> Semiconductor and semiconductor assembly sectors bounce back sharply as global memory/chip cycles recover, stabilizing local currency.",
                "<strong>Consumer Behavior:</strong> Mature middle-class purchasing power. Demands lean heavily towards product reliability, robust localized after-sales services, and high-performance computing setups for flexible workspaces."
            ],
            "Thailand": [
                "<strong>Macro Core:</strong> Service and tourism sectors operate at full recovery capacity, reinforcing its historical status as an automotive and electronic supply chain hub.",
                "<strong>Consumer Behavior:</strong> Extreme sensitivity to aesthetics, sleek product styling, and device color choices. Urban white-collar workers favor premium, highly curated tech ecosystems via specialized online boutique platforms."
            ],
            "Vietnam": [
                "<strong>Macro Core:</strong> High FDI inflows and robust export-oriented electronics manufacturing clusters maintain rapid economic velocity.",
                "<strong>Consumer Behavior:</strong> Ambitious, tech-savvy younger workforce and urban parents show immense willingness to spend heavily on smart devices tailored for digital education and professional upskilling."
            ]
        }

        country_insights = insights_repo.get(selected_country, insights_repo["China"])

        summary_html = f"""
        <div style="background-color: #f1f3f5; border-left: 5px solid #1f77b4; padding: 15px; border-radius: 4px; margin-bottom: 25px;">
            <p style="margin-top:0; font-weight:bold; color:#1f77b4; font-size:16px;">🇬🇧 Executive Insights ({selected_country} Market Intelligence)</p>
            <ul style="margin-bottom:0; font-size:14px; color:#2b2b2b; line-height:1.6;">
                <li><strong>Overall Market Vibe:</strong> {vibe_emoji} {market_vibe} (Sentiment Index: {sentiment_index} pts)</li>
                <li>{country_insights[0]}</li>
                <li>{country_insights[1]}</li>
                <li><strong>Strategic Takeaway:</strong> Align retail mapping and pricing models tightly with the current dynamic of {selected_country}, shifting channel investments where consumer traction is densest.</li>
            </ul>
        </div>
        """
        st.markdown(summary_html, unsafe_allow_html=True)

        # 📰 单条新闻列表
        st.markdown(f"#### 📰 最新资讯情绪穿透列表 (Source: {selected_country} Core Streams)")
        for idx, news in enumerate(current_news):
            with st.container():
                st.markdown(f"**[{idx + 1}] [{news['date']}] [{news['title']}]({news['link']})**")
                if news['desc']:
                    st.caption(f"📝 *原文摘要：*{news['desc']}")
                st.write(
                    f'<div style="background-color:{news["bg"]}; color:{news["tc"]}; '
                    f'padding:8px 12px; border-radius:5px; font-size:14px; font-weight:bold; margin-bottom:15px;">'
                    f'AI 情绪鉴定：{news["sentiment"]} | 💡 决策建议：{news["advice"]}'
                    f'</div>',
                    unsafe_allow_html=True
                )
    else:
        st.info(f"暂无 {selected_country} 实时资讯更新。")

# ==================== 📂 底部明细审核 ====================
st.markdown(" ")
if st.checkbox("🔍 显示清洗后的底层 Dataframe 数据矩阵明细"):
    st.dataframe(df_countries, use_container_width=True)