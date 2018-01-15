# coding='utf-8'
# 定义程序路由
from datetime import datetime
from flask import render_template,session,redirect,url_for
from flask_login import login_required
from ..decorators import admin_required,permission_required
from . import main
from .forms import NameForm
from .. import db
from ..models import User,Permission

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

'''
@main.route('/user/<username>')
def user(username):
        user = User.query.filter_by(username=username).first_or_404()
        page = request.args.get('page', 1, type=int)
        pagination = user.posts.order_by(Post.timestamp.desc()).paginate(page, per_page=current_app.config['FLASKY_POSTS_PER_PAGE'],error_out=False)
        posts = pagination.items
        return render_template('user.html', user=user, posts=posts,pagination=pagination)
'''

