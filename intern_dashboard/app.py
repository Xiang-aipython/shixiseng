import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import matplotlib.pyplot as plt
from collections import Counter
import numpy as np
import os

# 设置matplotlib使用中文字体
plt.rcParams['font.sans-serif'] = ['SimHei', 'DejaVu Sans']  # 用来正常显示中文标签
plt.rcParams['axes.unicode_minus'] = False  # 用来正常显示负号

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
        font-weight: bold;
    }
    .metric-card {
        background-color: #f0f2f6;
        padding: 1rem;
        border-radius: 10px;
        text-align: center;
        border-left: 4px solid #1f77b4;
    }
    .section-header {
        color: #1f77b4;
        border-bottom: 2px solid #1f77b4;
        padding-bottom: 0.5rem;
        margin-top: 2rem;
    }
</style>
""", unsafe_allow_html=True)

# 数据加载函数
@st.cache_data
def load_data():
    """加载数据 - 修复路径问题"""
    try:
        # 获取当前文件所在目录
        current_dir = os.path.dirname(os.path.abspath(__file__))
        data_path = os.path.join(current_dir, 'data', 'shixiseng_data_analyzer_jobs_20251112_165150.xlsx')
        
        if os.path.exists(data_path):
            df = pd.read_excel(data_path)
            from utils.data_cleaner import clean_data
            return clean_data(df)
        else:
            # 列出当前目录文件，帮助调试
            st.warning(f"文件不存在: {data_path}")
            st.info(f"当前目录文件: {os.listdir('.')}")
            if os.path.exists('data'):
                st.info(f"data目录文件: {os.listdir('data')}")
            return create_sample_data()
            
    except Exception as e:
        st.error(f"数据加载失败: {e}")
        return create_sample_data()

def create_sample_data():
    """创建示例数据"""
    sample_data = {
        '公司名称': ['快手', '字节跳动', '滴滴', '美团', '腾讯', '百度', '阿里巴巴', '京东'],
        '岗位名称': ['数据分析实习生', '数据运营实习生', '商业分析实习生', '数据产品实习生', '数据开发实习生', '数据挖掘实习生', '数据科学家实习生', 'BI分析师实习生'],
        '工作地点': ['北京', '上海', '北京', '北京', '深圳', '北京', '杭州', '北京'],
        '日薪': ['200-300/天', '200/天', '150-200/天', '180-250/天', '250-300/天', '200-280/天', '300-400/天', '180-220/天'],
        '职位描述': [
            '需要SQL Python Excel 数据分析 统计学',
            'SQL Tableau 数据可视化 业务分析',
            'Python SQL 机器学习 数据挖掘', 
            'Excel PPT SQL 产品思维',
            'Python Java SQL 大数据',
            'Python SQL 数据挖掘 算法',
            'Python R 机器学习 深度学习',
            'SQL Excel PowerBI 业务分析'
        ],
        '公司性质': ['民营企业', '民营企业', '民营企业', '民营企业', '民营企业', '民营企业', '民营企业', '民营企业'],
        '公司规模': ['2000人以上', '2000人以上', '2000人以上', '2000人以上', '2000人以上', '2000人以上', '2000人以上', '2000人以上'],
        '岗位链接': ['https://example.com'] * 8
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

# 实习时长筛选
duration_options = ['全部', '3个月', '4个月', '6个月', '6个月以上']
selected_duration = st.sidebar.selectbox("实习时长", duration_options, index=0)

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
st.markdown("### 📈 核心指标")

col1, col2, col3, col4 = st.columns(4)

with col1:
    total_jobs = len(filtered_df)
    st.metric("📊 总岗位数", f"{total_jobs}个", delta=f"{len(filtered_df)-len(df)}" if len(filtered_df) != len(df) else None)

with col2:
    if not filtered_df['avg_salary'].isna().all() and len(filtered_df) > 0:
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
st.markdown("### 📊 分布分析")

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
        fig_city.update_layout(showlegend=False)
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
    else:
        st.info("暂无薪资数据")

# 第二行：技能分析
st.markdown("---")
st.markdown("### 🛠️ 技能需求分析")

col1, col2 = st.columns(2)

with col1:
    # 技能词频 - 主要技能排行
    all_skills_filtered = [skill for sublist in filtered_df['skills'] for skill in sublist if skill]
    if all_skills_filtered:
        skill_counts = Counter(all_skills_filtered)
        
        fig_skills = px.bar(
            x=list(skill_counts.values()),
            y=list(skill_counts.keys()),
            orientation='h',
            title="📊 技能需求排行",
            labels={'x': '出现频次', 'y': '技能'},
            color=list(skill_counts.values()),
            color_continuous_scale='viridis'
        )
        fig_skills.update_layout(showlegend=False)
        st.plotly_chart(fig_skills, use_container_width=True)
    else:
        st.info("暂无技能数据")

with col2:
    # 技能分布饼图 - 替代词云
    all_skills_filtered = [skill for sublist in filtered_df['skills'] for skill in sublist if skill]
    if all_skills_filtered:
        skill_counts = Counter(all_skills_filtered)
        
        # 只显示前8个技能，其他归为"其他"
        top_skills = dict(sorted(skill_counts.items(), key=lambda x: x[1], reverse=True)[:8])
        other_count = sum(skill_counts.values()) - sum(top_skills.values())
        
        if other_count > 0:
            top_skills['其他'] = other_count
        
        fig_pie = px.pie(
            values=list(top_skills.values()),
            names=list(top_skills.keys()),
            title="🔤 技能分布占比",
            hole=0.3
        )
        fig_pie.update_traces(textposition='inside', textinfo='percent+label')
        st.plotly_chart(fig_pie, use_container_width=True)
    else:
        st.info("暂无技能数据")

# 第三行：公司分析
st.markdown("---")
st.markdown("### 🏢 公司分析")

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
    else:
        st.info("暂无公司规模数据")

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
        fig_type.update_layout(showlegend=False)
        st.plotly_chart(fig_type, use_container_width=True)
    else:
        st.info("暂无公司性质数据")

# 第四行：热门公司
st.markdown("---")
st.markdown("### 🏆 热门公司排行")

if not filtered_df.empty:
    company_counts = filtered_df['公司名称'].value_counts().head(10)
    fig_company = px.bar(
        x=company_counts.values,
        y=company_counts.index,
        orientation='h',
        title="🔥 招聘岗位最多的公司TOP10",
        labels={'x': '岗位数量', 'y': '公司名称'},
        color=company_counts.values,
        color_continuous_scale='reds'
    )
    fig_company.update_layout(showlegend=False)
    st.plotly_chart(fig_company, use_container_width=True)

# 岗位详情表格
st.markdown("---")
st.markdown("### 📋 岗位详情列表")

if not filtered_df.empty:
    st.markdown(f"显示 **{len(filtered_df)}** 个匹配岗位")
    
    # 简化显示列
    display_columns = ['公司名称', '岗位名称', 'clean_city', '日薪', 'skills', '岗位链接']
    display_df = filtered_df[display_columns].copy()
    display_df['skills'] = display_df['skills'].apply(lambda x: ', '.join(x) if x else '无')
    display_df = display_df.rename(columns={'clean_city': '工作地点'})
    
    # 分页显示
    page_size = 10
    total_pages = max(1, (len(display_df) + page_size - 1) // page_size)
    
    page_number = st.number_input("页码", min_value=1, max_value=total_pages, value=1)
    start_idx = (page_number - 1) * page_size
    end_idx = min(start_idx + page_size, len(display_df))
    
    st.dataframe(
        display_df.iloc[start_idx:end_idx],
        use_container_width=True,
        height=400
    )
    
    st.caption(f"显示第 {start_idx + 1} - {end_idx} 条，共 {len(display_df)} 条记录")
    
    # 数据下载
    csv = display_df.to_csv(index=False, encoding='utf-8-sig')
    st.download_button(
        label="📥 下载筛选后数据(CSV)",
        data=csv,
        file_name="数据分析实习岗位.csv",
        mime="text/csv",
        use_container_width=True
    )
else:
    st.warning("🚫 没有找到匹配的岗位，请调整筛选条件")

# 使用说明
with st.expander("💡 使用说明"):
    st.markdown("""
    ### 使用指南
    
    1. **数据筛选**：使用左侧筛选器按城市、薪资、技能等条件筛选岗位
    2. **数据可视化**：查看上方的图表了解岗位分布、技能需求等趋势
    3. **岗位详情**：在下方表格中查看具体的岗位信息
    4. **数据导出**：点击下载按钮导出筛选后的数据
    
    ### 功能特点
    
    - 🔍 **智能筛选**：多维度精准筛选
    - 📊 **可视化分析**：图表直观展示数据趋势
    - 🛠️ **技能洞察**：分析市场需求技能
    - 📥 **数据导出**：支持CSV格式导出
    - 📱 **响应式设计**：适配不同设备
    
    ### 技术支持
    
    如遇问题，请检查：
    - 数据文件是否在正确位置
    - 网络连接是否正常
    - 浏览器是否支持现代Web技术
    """)

# 页脚
st.markdown("---")
st.markdown("""
<div style='text-align: center; color: #666;'>
    <p>💡 <b>数据来源</b>: 实习僧 | <b>更新日期</b>: 2025-11-12 | <b>版本</b>: 2.0</p>
    <p>🚀 基于Streamlit构建 | 优化的可视化体验</p>
</div>
""", unsafe_allow_html=True)

# 调试信息（可注释掉）
if st.sidebar.checkbox("显示调试信息", False):
    st.sidebar.write("### 调试信息")
    st.sidebar.write(f"数据行数: {len(df)}")
    st.sidebar.write(f"筛选后行数: {len(filtered_df)}")
    st.sidebar.write(f"技能列表: {all_skills_filtered[:10]}")
