from flask import render_template
from . import main

@main.app_errorhandler(404)
def page_not_found(e):
	return render_template('404.html'),404

# 为了注册程序全局错误处理程序.若使用errorhandler修饰器,则只有蓝本中的错误才能触发处理程序
@main.app_errorhandler(500)
def internal_server_error(e):
	return render_template('500.html'),500
