#!/bin/bash

echo "正在设置数据分析实习仪表盘..."

# 创建必要的目录
mkdir -p .streamlit
mkdir -p utils

# 安装Python依赖
pip install -r requirements.txt

echo "设置完成！"
echo "运行命令: streamlit run app.py"