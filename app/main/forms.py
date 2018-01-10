# coding='utf-8'
# 表单对象
from flask_wtf import FlaskForm
from wtforms import StringField,SubmitField
from wtforms.validators import Required

class NameForm(FlaskForm):
	name = StringField("用户名",validators = [Required()])
	submit = SubmitField('提交')

