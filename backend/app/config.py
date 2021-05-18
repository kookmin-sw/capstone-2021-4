import os
BASEDIR = os.path.abspath(os.path.dirname(__file__))
TOP_LEVEL_DIR = os.path.abspath(os.curdir)
from botocore.config import Config as AWSConfig

class Config(object):
    TZ="Asia/Seoul"
    DEBUG = True
    TESTING = False
    CSRF_ENABLED = True
    SECRET_KEY =  os.environ.get("SECRET_KEY")
    BCRYPT_LOG_ROUNDS = 15
    MAIL_SERVER = os.environ.get('MAIL_SERVER')
    MAIL_PORT = 465
    MAIL_USE_TLS = False
    MAIL_USE_SSL = True
    MAIL_USERNAME = os.environ.get('MAIL_USERNAME') or 'your-mandrill-username'
    MAIL_PASSWORD = os.environ.get('MAIL_PASSWORD') or 'your mandrill-password'
    MAIL_DEFAULT_SENDER = os.environ.get('MAIL_DEFAULT_SENDER') or 'your@default-mail.com'
    OAUTH_GOOGLE_CLIENTID= os.environ.get("OAUTH_GOOGLE_CLIENTID")
    OAUTH_GOOGLE_SECRETKEY=os.environ.get("OAUTH_GOOGLE_SECRETKEY")
    AWS_CONFIG = AWSConfig(
        region_name = 'ap-northeast-2', 
        signature_version = 'v4',  
        retries = {
            'max_attempts': 10,
            'mode': 'standard'
        },
    )
    MAIN_DOMAIN_HOSTEDZONEID = os.getenv("HostedZoneId")
    SQLALCHEMY_DATABASE_URI =  os.getenv("SQLALCHEMY_DATABASE_URI")
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    
    def __init__(self):
        pass

class ProductionConfig(Config):
    DEBUG = False


class StagingConfig(Config):
    DEVELOPMENT = True
    DEBUG = True


class DevelopmentConfig(Config):
    DEVELOPMENT = True
    DEBUG = True
    

class TestingConfig(Config):
    TESTING = True
