# coding='utf-8'

# 记录所有依赖包及其精确的版本号
pip freeze > requirements.txt
# 创建完全副本
pip install -r requirements.txt

# 设置环境变量
export MAIL_USERNAME="..."
