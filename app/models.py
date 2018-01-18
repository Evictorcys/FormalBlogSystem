# coding='utf-8'
# 数据库模型
from werkzeug.security import generate_password_hash,check_password_hash
from flask_login import UserMixin,AnonymousUserMixin
from . import login_manager,db
from flask import current_app,request
from itsdangerous import TimedJSONWebSignatureSerializer as Serializer
import hashlib
from datetime import datetime
from markdown import markdown
import bleach

# 权限常量
class Permission:
    FOLLOW = 0x01
    COMMENT = 0x02
    WRITE_ARTICLES = 0x04
    MODERATE_COMMENTS = 0x08
    ADMINISTER = 0x80

# roles表
class Role(db.Model):
    __tablename__ = 'roles'
    id = db.Column(db.Integer,primary_key = True)
    name = db.Column(db.String(64),unique = True)
    default = db.Column(db.Boolean,default = False,index = True)
    permissions = db.Column(db.Integer)
    users = db.relationship('User',backref = 'role',lazy = 'dynamic')

    @staticmethod
    def insert_roles():
        roles = {
            'User':(Permission.FOLLOW|Permission.COMMENT|Permission.WRITE_ARTICLES,True),
            'Moderator':(Permission.FOLLOW|Permission.COMMENT|Permission.WRITE_ARTICLES|Permission.MODERATE_COMMENTS,False),
            'Administrator':(0xff,False),
        }
        for r in roles:
            role = Role.query.filter_by(name = r).first()
            if role is None:
                role = Role(name = r)
            role.permissions = roles[r][0]
            role.default = roles[r][1]
            db.session.add(role)
        db.session.commit()

# users表
class User(UserMixin,db.Model):
    __tablename__ = 'users'
    id = db.Column(db.Integer,primary_key = True)
    email = db.Column(db.String(64),unique = True,index = True)
    username = db.Column(db.String(64),unique = True,index =True)
    password_hash = db.Column(db.String(128))
    role_id = db.Column(db.Integer,db.ForeignKey('roles.id'))
    posts = db.relationship('Post',backref = 'author',lazy = 'dynamic')
    confirmed = db.Column(db.Boolean,default = False)
    avatar_hash = db.Column(db.String(32))

    # 真实姓名
    realname = db.Column(db.String(64))
    # 所在地
    location = db.Column(db.String(64))
    # 自我介绍
    aboutme = db.Column(db.Text())
    # 注册日期
    registrationdate = db.Column(db.DateTime(),default = datetime.utcnow)
    # 最后访问日期
    lastvisitdate = db.Column(db.DateTime(),default = datetime.utcnow)

    def __init__(self,**kwargs):
        # 先调用基类构造函数
        super(User,self).__init__(**kwargs)
        # 若基类对象未定义角色
        if self.role is None:
            # 根据电子邮件地址将其设为管理员
            if self.email == current_app.config['ADMIN_MAIL']:
                self.role = Role.query.filter_by(permissions = 0xff).first()
            # 设为默认角色
            if self.role is None:
                self.role = Role.query.filter_by(default = True).first()

        # 缓存md5以生成Gravartar URL
        if self.email is not None and self.avatar_hash is None:
            self.avatar_hash = self.gravatar_hash()

    @property
    def password(self):
         raise AttributeError('password is not a readable attribute')

    @password.setter
    def password(self,password):
        self.password_hash = generate_password_hash(password)

    def verify_password(self,password):
        return check_password_hash(self.password_hash,password)

    def generate_confirmation_token(self,expiration = 3600):
        s = Serializer(current_app.config['SECRET_KEY'],expiration)
        return s.dumps({'confirm':self.id})

    def confirm(self,token):
        s = Serializer(current_app.config['SECRET_KEY'])
        try:
            data = s.loads(token)
        except:
            return False
        if data.get('confirm')!=self.id:
            return False
        self.confirmed = True
        db.session.add(self)
        return True

    def generate_reset_token(self, expiration=3600):
        s = Serializer(current_app.config['SECRET_KEY'], expiration)
        return s.dumps({'reset': self.id}).decode('utf-8')

    @staticmethod
    def reset_password(token, new_password):
        s = Serializer(current_app.config['SECRET_KEY'])
        try:
            data = s.loads(token.encode('utf-8'))
        except:
            return False
        user = User.query.get(data.get('reset'))
        if user is None:
            return False
        user.password = new_password
        db.session.add(user)
        return True

    def generate_email_change_token(self, new_email, expiration=3600):
        s = Serializer(current_app.config['SECRET_KEY'], expiration)
        return s.dumps({'change_email': self.id, 'new_email' : new_email}).decode('utf-8')

    def change_email(self, token):
        s = Serializer(current_app.config['SECRET_KEY'])
        try:
            data = s.loads(token.encode('utf-8'))
        except:
            return False
        if data.get('change_email') != self.id:
            return False
        new_email = data.get('new_email')
        if new_email is None:
            return False
        if self.query.filter_by(email=new_email).first() is not None:
            return False
        self.email = new_email
        self.avatar_hash = self.gravatar_hash()
        db.session.add(self)
        return True

    def can(self,permissions):
        '''检查用户是否有指定权限'''
        return self.role is not None and \
                (self.role.permissions &permissions) == permissions

    def is_administrator(self):
        return self.can(Permission.ADMINISTER)

    # 刷新用户最后访问时间
    def ping(self):
        self.last_visit_date = datetime.utcnow()
        db.session.add(self)

    def gravatar_hash(self):
        return hashlib.md5(self.email.lower().encode('utf-8')).hexdigest()

    # 用户头像:生成Gravatar URL
    def gravatar(self, size=100, default='identicon', rating='g'):
        if request.is_secure:
            url = 'https://secure.gravatar.com/avatar'
        else:
            url = 'http://www.gravatar.com/avatar'
        hash = self.avatar_hash or hasnlib.md5(self.email.encode('utf-8')).hexdigest()
        return '{url}/{hash}?s={size}&d={default}&r={rating}'.format(url = url, \
                hash = hash, size = size, default = default,rating = rating)

    # 生成虚拟用户
    @staticmethod
    def generate_fake(count = 100):
        from sqlalchemy.exc import IntegrityError
        from random import seed
        import forgery_py

        seed()
        for i in range(count):
            u = User(email = forgery_py.internet.email_address(),
                     username = forgery_py.internet.user_name(True),
                     password = forgery_py.lorem_ipsum.word(),
                     confirmed = True,
                     realname = forgery_py.name.full_name(),
                     location = forgery_py.address.city(),
                     aboutme = forgery_py.lorem_ipsum.sentence(),
                     registrationdate = forgery_py.date.date(True))
            db.session.add(u)
            try:
                db.session.commit()
            except IntegrityError:
                db.session.rollback()


# 未登录用户
class AnonymousUser(AnonymousUserMixin):
    def can(self,permission):
        return False

    def is_administrator(self):
         return False

# 将其设为用户未登录时current_user的值
login_manager.anonymous_user = AnonymousUser

# 文章模型
class Post(db.Model):
    __tablename__ = 'posts'
    id = db.Column(db.Integer,primary_key = True)
    body = db.Column(db.Text)
    timestamp = db.Column(db.DateTime,index = True,default = datetime.utcnow)
    author_id = db.Column(db.Integer,db.ForeignKey('users.id'))
    body_html = db.Column(db.Text)

    # 生成虚拟博客文章
    @staticmethod
    def generate_fake(count = 300):
        from random import seed,randint
        import forgery_py

        seed()
        user_count = User.query.count()
        for i in range(count):
            u = User.query.offset(randint(0,user_count - 1)).first()
            p = Post(body = forgery_py.lorem_ipsum.sentences(randint(1,3)),
                     timestamp = forgery_py.date.date(True),
                     author = u)
            db.session.add(p)
            db.session.commit()

    # 将Markdown转化为html
    @staticmethod
    def on_changed_body(target,value,oldvalue,initiator):
        allowed_tags = ['a','abbr','acronym','b', 'blockquote', 'code',
                        'em', 'i', 'li', 'ol', 'pre', 'strong', 'ul',
                        'h1', 'h2', 'h3', 'p']
        target.body_html = bleach.linkify(bleach.clean(
            markdown(value,output_format = 'html'),
            tags = allowed_tags,strip = True))

# 函数注册在Post.body字段上,是set事件的监听程序
db.event.listen(Post.body, 'set', Post.on_changed_body)

@login_manager.user_loader
def load_user (user_id):
	return User.query.get(int(user_id))

