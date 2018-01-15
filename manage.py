# coding='utf-8'
### !/usr/bin/python3
# 加入shebang声明,故可通过./manage.py执行脚本
import os
from app import create_app,db
from app.models import User,Role
from flask_script import Manager,Shell
from flask_migrate import Migrate,MigrateCommand

# 读取配置名或使用默认配置
app = create_app(os.getenv('FLASK_CONFIG') or 'default')
manager = Manager(app)
migrate = Migrate(app,db)

def make_shell_context():
	return dict(app = app,db = db,User = User,Role = Role)

manager.add_command('shell',Shell(make_context = make_shell_context))
manager.add_command('db',MigrateCommand)

# 修饰函数就是命令名
@manager.command
def test():
	"""Run the unit test"""
	import unittest
	tests = unittest.TestLoader().discover('tests')
	unittest.TextTestRunner(verbosity = 2).run(tests)

if __name__ == '__main__':
	manager.run()
