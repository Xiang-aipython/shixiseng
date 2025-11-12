import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from wordcloud import WordCloud
import matplotlib.pyplot as plt
from collections import Counter
import numpy as np
import os
import base64

# 页面设置
st.set_page_config(
    page_title="数据分析实习岗位洞察",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# 自定义CSS
st.markdown("""
<style>
    .main-header {
        font-size: 2.5rem;
        color: #1f77b4;
        text-align: center;
        margin-bottom: 2rem;
    }
    .metric-card {
        background-color: #f0f2f6;
        padding: 1rem;
        border-radius: 10px;
        text-align: center;
    }
</style>
""", unsafe_allow_html=True)


# 数据加载函数
@st.cache_data
def load_data():
    """加载并清洗数据 - 适配部署环境"""
    try:
        # 尝试多个可能的数据路径
        possible_paths = [
            'data/shixiseng_data_analyzer_jobs_20251112_165150.xlsx',
            './data/shixiseng_data_analyzer_jobs_20251112_165150.xlsx',
            'shixiseng_data_analyzer_jobs_20251112_165150.xlsx',
            '../data/shixiseng_data_analyzer_jobs_20251112_165150.xlsx'
        ]

        for path in possible_paths:
            if os.path.exists(path):
                df = pd.read_excel(path)
                # 动态导入清洗模块
                from utils.data_cleaner import clean_data
                return clean_data(df)

        # 如果找不到文件，显示错误但继续运行
        st.error("⚠️ 未找到数据文件，显示示例数据")
        return create_sample_data()

    except Exception as e:
        st.error(f"数据加载失败: {e}")
        return create_sample_data()


def create_sample_data():
    """创建示例数据"""
    sample_data = {
        '公司名称': ['快手', '字节跳动', '滴滴', '美团', '腾讯'],
        '岗位名称': ['数据分析实习生', '数据运营实习生', '商业分析实习生', '数据产品实习生', '数据开发实习生'],
        '工作地点': ['北京', '上海', '北京', '北京', '深圳'],
        '日薪': ['200-300/天', '200/天', '150-200/天', '180-250/天', '250-300/天'],
        '职位描述': ['需要SQL Python Excel', 'SQL Tableau', 'Python SQL', 'Excel PPT SQL', 'Python Java SQL'],
        '公司性质': ['民营企业', '民营企业', '民营企业', '民营企业', '民营企业'],
        '公司规模': ['2000人以上', '2000人以上', '2000人以上', '2000人以上', '2000人以上'],
        '岗位链接': ['https://example.com', 'https://example.com', 'https://example.com', 'https://example.com',
                     'https://example.com']
    }
    df = pd.DataFrame(sample_data)
    from utils.data_cleaner import clean_data
    return clean_data(df)


# 标题
st.markdown('<h1 class="main-header">📊 数据分析实习岗位洞察仪表盘</h1>', unsafe_allow_html=True)
st.markdown("基于实习僧数据的实时分析平台 | 数据更新: 2025-11-12")

# 加载数据
with st.spinner('正在加载数据...'):
    df = load_data()

if df.empty:
    st.error("无法加载数据，请检查数据文件")
    st.stop()

# 侧边栏筛选器
st.sidebar.header("🔍 数据筛选")

# 城市筛选
cities = ['全部'] + sorted(df['clean_city'].dropna().unique().tolist())
selected_city = st.sidebar.selectbox("选择城市", cities, index=0)

# 薪资筛选
if not df['avg_salary'].isna().all():
    max_salary_val = int(df['avg_salary'].max()) + 50
    min_salary, max_salary = st.sidebar.slider(
        "日薪范围(元)",
        min_value=0,
        max_value=max_salary_val,
        value=(0, min(500, max_salary_val))
    )
else:
    min_salary, max_salary = 0, 500

# 技能筛选
all_skills = list(set([skill for sublist in df['skills'] for skill in sublist if skill]))
selected_skills = st.sidebar.multiselect("技能要求", all_skills)

# 公司性质筛选
company_types = ['全部'] + sorted(df['公司性质'].dropna().unique().tolist())
selected_type = st.sidebar.selectbox("公司性质", company_types, index=0)

# 应用筛选
filtered_df = df.copy()
if selected_city != '全部':
    filtered_df = filtered_df[filtered_df['clean_city'] == selected_city]

if not df['avg_salary'].isna().all():
    filtered_df = filtered_df[
        (filtered_df['avg_salary'] >= min_salary) &
        (filtered_df['avg_salary'] <= max_salary)
        ]

if selected_skills:
    filtered_df = filtered_df[
        filtered_df['skills'].apply(lambda x: any(skill in x for skill in selected_skills))
    ]

if selected_type != '全部':
    filtered_df = filtered_df[filtered_df['公司性质'] == selected_type]

# KPI指标行
st.markdown("---")
col1, col2, col3, col4 = st.columns(4)

with col1:
    total_jobs = len(filtered_df)
    st.metric("📊 总岗位数", f"{total_jobs}个")

with col2:
    if not filtered_df['avg_salary'].isna().all():
        avg_salary = filtered_df['avg_salary'].mean()
        st.metric("💰 平均日薪", f"¥{avg_salary:.0f}元")
    else:
        st.metric("💰 平均日薪", "数据缺失")

with col3:
    city_count = filtered_df['clean_city'].nunique()
    st.metric("🏙️ 覆盖城市", f"{city_count}个")

with col4:
    company_count = filtered_df['公司名称'].nunique()
    st.metric("🏢 招聘公司", f"{company_count}家")

# 第一行：分布图表
st.markdown("---")
st.subheader("📈 分布分析")

col1, col2 = st.columns(2)

with col1:
    # 城市分布
    if not filtered_df.empty:
        city_counts = filtered_df['clean_city'].value_counts().head(10)
        fig_city = px.bar(
            x=city_counts.values,
            y=city_counts.index,
            orientation='h',
            title="🏙️ 热门城市TOP10",
            labels={'x': '岗位数量', 'y': '城市'},
            color=city_counts.values,
            color_continuous_scale='blues'
        )
        st.plotly_chart(fig_city, use_container_width=True)

with col2:
    # 薪资分布
    if not filtered_df['avg_salary'].isna().all() and not filtered_df.empty:
        fig_salary = px.box(
            filtered_df,
            y='avg_salary',
            title="💰 日薪分布箱线图",
            labels={'avg_salary': '日薪(元)'}
        )
        st.plotly_chart(fig_salary, use_container_width=True)

# 第二行：技能分析
st.markdown("---")
st.subheader("🛠️ 技能需求分析")

col1, col2 = st.columns(2)

with col1:
    # 技能词频
    all_skills_filtered = [skill for sublist in filtered_df['skills'] for skill in sublist if skill]
    if all_skills_filtered:
        skill_counts = Counter(all_skills_filtered)

        fig_skills = px.bar(
            x=list(skill_counts.keys()),
            y=list(skill_counts.values()),
            title="📊 技能需求排行",
            labels={'x': '技能', 'y': '出现频次'},
            color=list(skill_counts.values()),
            color_continuous_scale='viridis'
        )
        st.plotly_chart(fig_skills, use_container_width=True)

with col2:
    # 词云
    if all_skills_filtered:
        try:
            wordcloud = WordCloud(
                width=800,
                height=400,
                background_color='white',
                colormap='plasma',
                max_words=50
            ).generate(' '.join(all_skills_filtered))

            fig, ax = plt.subplots(figsize=(10, 5))
            ax.imshow(wordcloud, interpolation='bilinear')
            ax.axis('off')
            ax.set_title('🔤 技能词云图')
            st.pyplot(fig)
        except Exception as e:
            st.warning(f"词云生成失败: {e}")

# 第三行：公司分析
st.markdown("---")
st.subheader("🏢 公司分析")

col1, col2 = st.columns(2)

with col1:
    # 公司规模分布
    if 'company_size' in filtered_df.columns and not filtered_df.empty:
        size_counts = filtered_df['company_size'].value_counts()
        fig_size = px.pie(
            values=size_counts.values,
            names=size_counts.index,
            title="📏 公司规模分布",
            hole=0.4
        )
        st.plotly_chart(fig_size, use_container_width=True)

with col2:
    # 公司性质
    if not filtered_df.empty:
        type_counts = filtered_df['公司性质'].value_counts()
        fig_type = px.bar(
            x=type_counts.index,
            y=type_counts.values,
            title="🏛️ 公司性质分布",
            labels={'x': '公司性质', 'y': '数量'},
            color=type_counts.values,
            color_continuous_scale='teal'
        )
        st.plotly_chart(fig_type, use_container_width=True)

# 岗位详情表格
st.markdown("---")
st.subheader("📋 岗位详情列表")
st.markdown(f"显示 **{len(filtered_df)}** 个匹配岗位")

if not filtered_df.empty:
    # 简化显示列
    display_columns = ['公司名称', '岗位名称', 'clean_city', '日薪', 'skills', '岗位链接']
    display_df = filtered_df[display_columns].copy()
    display_df['skills'] = display_df['skills'].apply(lambda x: ', '.join(x) if x else '无')
    display_df = display_df.rename(columns={'clean_city': '工作地点'})

    # 显示表格
    st.dataframe(
        display_df,
        use_container_width=True,
        height=400
    )

    # 数据下载
    csv = display_df.to_csv(index=False)
    st.download_button(
        label="📥 下载筛选后数据(CSV)",
        data=csv,
        file_name="数据分析实习岗位.csv",
        mime="text/csv",
        use_container_width=True
    )
else:
    st.warning("没有找到匹配的岗位，请调整筛选条件")

# 页脚
st.markdown("---")
st.markdown("""
<div style='text-align: center; color: #666;'>
    <p>💡 <b>数据来源</b>: 实习僧 | <b>更新日期</b>: 2025-11-12</p>
    <p>🚀 基于Streamlit构建 | 如有问题请联系技术支持</p>
</div>
""", unsafe_allow_html=True)