# coding='utf-8'
# 数据库模型
from werkzeug.security import generate_password_hash,check_password_hash
from flask_login import UserMixin,AnonymousUserMixin
from . import login_manager,db
from flask import current_app
from itsdangerous import TimedJSONWebSignatureSerializer as Serializer

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
    confirmed = db.Column(db.Boolean,default = False)
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

    def can(self,permissions):
        '''检查用户是否有指定权限'''
        return self.role is not None and \
                (self.role.permissions &permissions) == permissions

    def is_administrator(self):
        return self.can(Permission.ADMINSTER)

# 未登录用户
class AnonymousUser(AnonymousUserMixin):
    def can(self,permission):
        return False

    def is_administrator(self):
         return False

# 将其设为用户未登录时current_user的值
login_manager.anonymous_user = AnonymousUser

@login_manager.user_loader
def load_user (user_id):
	return User.query.get(int(user_id))

