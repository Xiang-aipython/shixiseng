import pandas as pd
import re


def clean_salary(salary_str):
    """清洗薪资数据"""
    if pd.isna(salary_str) or '面议' in str(salary_str):
        return None, None

    try:
        # 提取数字范围
        numbers = re.findall(r'(\d+)', str(salary_str))
        if len(numbers) >= 2:
            return int(numbers[0]), int(numbers[1])
        elif len(numbers) == 1:
            return int(numbers[0]), int(numbers[0])
        return None, None
    except:
        return None, None


def extract_skills(description):
    """从职位描述中提取技能关键词"""
    if pd.isna(description):
        return []

    desc_str = str(description).lower()
    skills = []

    skill_keywords = {
        'SQL': ['sql', 'hive'],
        'Python': ['python', 'pandas', 'numpy'],
        'Excel': ['excel', '数据透视表'],
        'Tableau': ['tableau'],
        'Power BI': ['power bi', 'powerbi'],
        'R': ['r语言', ' r '],
        'SPSS': ['spss'],
        'Java': ['java'],
        'PPT': ['ppt', 'powerpoint'],
        '统计分析': ['统计分析', '数据统计'],
        '数据可视化': ['数据可视化', '可视化'],
        '机器学习': ['机器学习', '深度学习']
    }

    for skill, keywords in skill_keywords.items():
        if any(keyword in desc_str for keyword in keywords):
            skills.append(skill)

    return skills


def clean_data(df):
    """主数据清洗函数"""
    df_clean = df.copy()

    # 薪资清洗
    salary_data = df_clean['日薪'].apply(clean_salary)
    df_clean['min_salary'] = salary_data.apply(lambda x: x[0] if x else None)
    df_clean['max_salary'] = salary_data.apply(lambda x: x[1] if x else None)
    df_clean['avg_salary'] = df_clean[['min_salary', 'max_salary']].mean(axis=1)

    # 技能提取
    df_clean['skills'] = df_clean['职位描述'].apply(extract_skills)

    # 城市清洗
    df_clean['clean_city'] = df_clean['工作地点'].str.split('/').str[0]
    df_clean['clean_city'] = df_clean['clean_city'].fillna('未知')

    # 公司规模标准化
    def clean_company_size(size):
        if pd.isna(size):
            return '未知'
        size_str = str(size)
        if '2000' in size_str:
            return '2000人以上'
        elif '500' in size_str:
            return '500-2000人'
        elif '150' in size_str:
            return '150-500人'
        elif '50' in size_str:
            return '50-150人'
        else:
            return '50人以下'

    df_clean['company_size'] = df_clean['公司规模'].apply(clean_company_size)

    return df_clean