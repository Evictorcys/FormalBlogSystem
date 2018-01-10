# coding='utf-8'
# 登录表单及用户注册表单
from flask_wtf import FlaskForm
from wtforms import StringField,PasswordField,BooleanField,SubmitField
from wtforms.validators import Required,Length,Email,Regexp,EqualTo
from wtforms import ValidationError
from ..models import User

class LoginForm(FlaskForm):
	email = StringField('邮箱:',validators = [Required(),Length(1,64),Email()])
	password = PasswordField('密码:',validators = [Required()])
	remember_me = BooleanField('记住我')
	submit = SubmitField('登录')

class RegistrationForm(FlaskForm):
	email = StringField('邮箱:',validators = [Required(),Length(1,64),Email()])
	username = StringField('用户名:',validators = [
		Required(),Length(1,64),Regexp('^[A-Za-z][A-Za-z0-9_]*$',0,
									   '用户名必须仅含字母、数字、下划线!')])
	password = PasswordField('密码:',validators = [
		Required(),EqualTo('password2',message = '两次密码必须相同!')])
	password2 = PasswordField('确认密码:',validators = [Required()])
	submit = SubmitField('注册')
	
	def validate_mail(self,field):
		if User.query.filter_by(email = field.data).first():
			raise ValidationError('该邮箱已被注册了!')

	def validate_username(self,field):
		if User.query.filter_by(username = field.data).first():
			raise ValidationError('该用户名已被使用了!')

class ChangePasswordForm(FlaskForm):
    old_password = PasswordField('旧密码:', validators=[Required()])
    password = PasswordField('新密码:', validators=[
        Required(), EqualTo('password2', message='Passwords must match.')])
    password2 = PasswordField('确认密码:',
                              validators=[Required()])
    submit = SubmitField('确认更改')


class PasswordResetRequestForm(FlaskForm):
    email = StringField('邮箱:', validators=[Required(), Length(1, 64),
                                             Email()])
    submit = SubmitField('重置密码')


class PasswordResetForm(FlaskForm):
    password = PasswordField('新密码:', validators=[
        Required(), EqualTo('password2', message='Passwords must match')])
    password2 = PasswordField('确认密码:', validators=[Required()])
    submit = SubmitField('确认修改')


class ChangeEmailForm(FlaskForm):
    email = StringField('新邮箱:', validators=[Required(), Length(1, 64),
                                                 Email()])
    password = PasswordField('密码:', validators=[Required()])
    submit = SubmitField('确认更改')

    def validate_email(self, field):
        if User.query.filter_by(email=field.data).first():
            raise ValidationError('该邮箱已被注册了!')
