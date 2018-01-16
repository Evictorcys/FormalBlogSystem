# coding='utf-8'
# 定义程序路由
from datetime import datetime
from flask import render_template,session,redirect,url_for,abort,flash,request,current_app,make_response
from flask_login import login_required,current_user
from ..decorators import admin_required,permission_required
from . import main
from .forms import NameForm,EditProfileForm,EditProfileAdminForm
from .. import db
from ..models import User,Permission,Role

# 蓝本中视图函数两点不同:
# 1)路由修饰器由蓝本提供;
# 2)url_for()函数用法不同,由于Flask会为蓝本中全部端点加上一个命名空间.
@main.route('/',methods = ['GET','POST'])
def index():
	form = NameForm()
	if form.validate_on_submit():
		# 
		return redirect(url_for('.index'))
	return render_template('index.html',form = form,name = session.get('name'),
		    		known = session.get('known',False),
                                current_time = datetime.utcnow())


@main.route('/admin')
@login_required
@admin_required
def for_admins_only():
    return "For adminstrators!"

@main.route('/moderator')
@login_required
@permission_required(Permission.MODERATE_COMMENTS)
def for_moderators_only():
    return "For comment moderators!"

# 个人资料编辑路由
@main.route('/edit-profile',methods=['GET','POST'])
@login_required
def edit_profile():
    form = EditProfileForm()
    if form.validate_on_submit():
        current_user.realname = form.realname.data
        current_user.location = form.location.data
        current_user.aboutme = form.aboutme.data
        db.session.add(current_user)
        flash('您的个人信息修改成功!')
        return redirect(url_for('.user',username = current_user.username))
    form.realname = current_user.realname
    form.location = current_user.location
    form.aboutme = current_user.aboutme
    return render_template('edit_profile.html',form = form)

# 管理员资料编辑路由
@main.route('/edit-profile/<int:id>', methods=['GET', 'POST'])
@login_required
@admin_required
def edit_profile_admin(id):
    user = User.query.get_or_404(id)
    form = EditProfileAdminForm(user=user)
    if form.validate_on_submit():
        user.email = form.email.data
        user.username = form.username.data
        user.confirmed = form.confirmed.data
        user.role = Role.query.get(form.role.data)
        user.realname = form.realname.data
        user.location = form.location.data
        user.aboutme = form.aboutme.data
        db.session.add(user)
        db.session.commit()
        flash('用户的个人信息已成功修改!')
        return redirect(url_for('.user',username = user.username))
    form.email.data = user.email
    form.username.data = user.username
    form.confirmed.data = user.confirmed
    form.role.data = user.role_id
    form.realname.data = user.realname
    form.location.data = user.location
    form.aboutme.data = user.aboutme
    return render_template('edit_profile.html',form = form,user = user)

# 资料页面的路由
@main.route('/user/<username>')
def user(username):
        user = User.query.filter_by(username=username).first_or_404()
        return render_template('user.html', user = user)

