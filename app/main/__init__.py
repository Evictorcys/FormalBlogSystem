# coding='utf-8'
# 创建蓝本
from flask import Blueprint

main = Blueprint('main',__name__)

# 放在末处,避免循环导入依赖
from . import views,errors