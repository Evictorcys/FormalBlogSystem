# coding='utf-8'
# 定义程序路由
from datetime import datetime
from flask import render_template,session,redirect,url_for,abort,flash,request,current_app,make_response
from flask_login import login_required,current_user
from ..decorators import admin_required,permission_required
from . import main
from .forms import NameForm,EditProfileForm,EditProfileAdminForm,PostForm
from .. import db
from ..models import User,Permission,Role,Post

# 蓝本中视图函数两点不同:
# 1)路由修饰器由蓝本提供;
# 2)url_for()函数用法不同,由于Flask会为蓝本中全部端点加上一个命名空间.
# 博客文章首页路由
@main.route('/',methods = ['GET','POST'])
def index():
    form = PostForm()
    if current_user.can(Permission.WRITE_ARTICLES) and form.validate_on_submit():
        post = Post(body = form.body.data,author = current_user._get_current_object())
        db.session.add(post)
        db.session.commit()
        return redirect(url_for('.index'))
    # 获取渲染的页数
    page = request.args.get('page', 1, type = int)
    query = Post.query
    # 分页paginate():per_page默认为20;error_out为True,页数超出范围返回404;为False,返回空列表
    pagination = query.order_by(Post.timestamp.desc()).paginate(
        page, per_page = current_app.config['EVICTOR_POSTS_PER_PAGE'],
        error_out = False)
    posts = pagination.items
    return render_template('index.html', form = form, posts = posts,
                           pagination = pagination)

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
    form.realname.data = current_user.realname
    form.location.data = current_user.location
    form.aboutme.data = current_user.aboutme
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
        posts = user.posts.order_by(Post.timestamp.desc()).all()
        return render_template('user.html', user = user,posts = posts)

# 文章的固定链接
@main.route('/post/<int:id>')
def post(id):
    post = Post.query.get_or_404(id)
    return render_template('post.html',posts = [post])

# 编辑博客文章路由
@main.route('/edit/<int:id>', methods=['GET', 'POST'])
@login_required
def edit(id):
    post = Post.query.get_or_404(id)
    if current_user != post.author and \
       not current_user.can(Permission.ADMINISTER):
        abort(403)
    form = PostForm()
    if form.validate_on_submit():
        post.body = form.body.data
        db.session.add(post)
        db.session.commit()
        flash('文章内容更新成功.')
        return redirect(url_for('.post',id = post.id))
    form.body.data = post.body
    return render_template('edit_post.html',form = form)

