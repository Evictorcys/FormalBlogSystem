# coding='utf-8'
# 表单对象
from flask_wtf import FlaskForm
from wtforms import StringField,SubmitField,TextAreaField,BooleanField,SelectField
from wtforms.validators import Required,Length,Email,Regexp
from wtforms import ValidationError
from ..models import User,Role

class NameForm(FlaskForm):
	name = StringField("用户名",validators = [Required()])
	submit = SubmitField('提交')

# 个人资料编辑表单
class EditProfileForm(FlaskForm):
    realname = StringField('真实姓名:',validators = [Length(0,64)])
    location = StringField('我的位置:',validators = [Length(0,64)])
    aboutme = TextAreaField('关于我:')
    submit = SubmitField('提交')

class EditProfileAdminForm(FlaskForm):
    email = StringField('邮箱:',validators = [Required(),Length(1,64),Email()])
    username = StringField('用户名:',validators = [Required(),Length(1,64), \
                                    Regexp('^[A-Za-z][A-Za-z0-9_]*$',0,'用户名必须仅包含字母数字及下划线')])
    confirmed = BooleanField('邮箱验证:')
    role = SelectField('用户角色:',coerce = int)
    realname = StringField('真实姓名:',validators = [Length(0,64)])
    location = StringField('位置:',validators = [Length(0,64)])
    aboutme = TextAreaField('关于我:')
    submit = SubmitField('提交')

    def __init__(self,user,*args,**kwargs):
        super(EditProfileAdminForm,self).__init__(*args,**kwargs)
        self.role.choices = [(role.id,role.name) for role in Role.query.order_by(Role.name).all()]
        self.user = user

    def validate_email(self, field):
        if field.data != self.user.email and \
           User.query.filter_by(email=field.data).first():
            raise ValidationError('该邮箱已被注册!')

    def validate_username(self, field):
        if field.data != self.user.username and \
        User.query.filter_by(username=field.data).first():
            raise ValidationError('该用户名已被使用!')


