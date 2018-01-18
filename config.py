# coding='utf-8'
# 配置文件
import os

class Config:
    """通用配置"""
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'Default Secret Key of Evictor'
    SQLALCHEMY_COMMIT_ON_TEARDOWN = True
    MAIL_SUBJECT_PREFIX = '[FormalBlogSystem]'
    MAIL_SENDER = 'Adminstrator <e2856527729@163.com>'
    ADMIN_MAIL = os.environ.get('ADMIN_MAIL')
    EVICTOR_POSTS_PER_PAGE = 20

    @staticmethod
    def init_app(app):
        pass

class DevelopmentConfig(Config):
    """开发环境配置"""
    DEBUG = True
    MAIL_SERVER = 'smtp.163.com'
    MAIL_PORT = 465
    MAIL_USE_SSL = True
    MAIL_USERNAME = os.environ.get('MAIL_USERNAME')
    MAIL_PASSWORD = os.environ.get('MAIL_PASSWORD')
    SQLALCHEMY_DATABASE_URI = os.environ.get('DEV_DATABASE_URL')

class TestingConfig(Config):
    """测试环境配置"""
    TESTING = True
    SQLALCHEMY_DATABASE_URI = os.environ.get('TEST_DATABASE_URL')

class ProductionConfig(Config):
    """生产环境配置"""
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL')

config = {
    'development':DevelopmentConfig,
    'testing':TestingConfig,
    'production':ProductionConfig,

    'default':DevelopmentConfig
}
