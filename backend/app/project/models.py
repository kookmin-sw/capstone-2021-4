from project import app, db, bcrypt
from sqlalchemy.ext.hybrid import hybrid_property, hybrid_method
import datetime
from dataclasses import dataclass
import jwt


class User(db.Model):
    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    email = db.Column(db.String(60), unique=True, nullable=False)
    _password = db.Column(db.Binary(60), nullable=False)
    authenticated = db.Column(db.Boolean, default=False)
    email_confirmation_sent_on = db.Column(db.DateTime, nullable=True)
    email_confirmed = db.Column(db.Boolean, nullable=True, default=False)
    email_confirmed_on = db.Column(db.DateTime, nullable=True)
    registered_on = db.Column(db.DateTime, nullable=True)
    last_logged_in = db.Column(db.DateTime, nullable=True)
    current_logged_in = db.Column(db.DateTime, nullable=True)
    role = db.Column(db.String(60), default='user')

    items = db.relationship('Items', cascade = "all,delete", backref='user', lazy='dynamic')
    clouds = db.relationship('Cloud', cascade = "all,delete" ,backref='user')
    vpc = db.relationship('VPC', cascade = "all, delete", backref="user")
    keypairs = db.relationship('Keypair', cascade = "all, delete", backref="user")
    

    def __json__(self):
        return ['id', 'email', '_password', 'authenticated', 'email_confirmation_sent_on', 
        'email_confirmed', 'email_confirmed_on', 'registered_on', 'last_logged_in', 'current_logged_in',
        'role', 'items']

    def __init__(self, email, password, email_confirmation_sent_on=None, role='user'):
        self.email = email
        self.password = password
        self.authenticated = False
        self.email_confirmation_sent_on = email_confirmation_sent_on
        self.email_confirmed = False
        self.email_confirmed_on = None
        self.registered_on = datetime.datetime.now()
        self.last_logged_in = None
        self.current_logged_in = datetime.datetime.now()
        self.role = role

    @hybrid_property
    def password(self):
        return self._password

    @password.setter
    def password(self, password):
        self._password = bcrypt.generate_password_hash(password)

    @hybrid_method
    def is_correct_password(self, password):
        return bcrypt.check_password_hash(self.password, password)

    @property
    def is_authenticated(self):
        """Return True if the user is authenticated."""
        return self.authenticated

    @property
    def is_active(self):
        """Always True, as all users are active."""
        return True

    @property
    def is_email_confirmed(self):
        """Return True if the user confirmed their email address."""
        return self.email_confirmed

    @property
    def is_anonymous(self):
        """Always False, as anonymous users aren't supported."""
        return False

    def get_id(self):
        """Return the email address to satisfy Flask-Login's requirements."""
        """Requires use of Python 3"""
        return str(self.id)

    def __repr__(self):
        return '<User {}>'.format(self.email)

    def encode_auth_token(self, user_id):
        """
        Generates the Auth Token
        :return: string
        """
        
        try:
            payload = {
                'exp': datetime.datetime.utcnow() + datetime.timedelta(days=0, seconds=5),
                'iat': datetime.datetime.utcnow(),
                'sub': user_id
            }

            # print("SECRET KEY{}".format(app.config.get("SECRET_KEY")))
            return jwt.encode(
                payload,
                app.config.get("SECRET_KEY"),
                algorithm='HS256'
            )
        except Exception as e:
            print("Error")
            return e

    


class Items(db.Model):
    __tablename__ = 'items'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(25), nullable=False)
    notes = db.Column(db.String(25), nullable=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'))

    def __init__(self, name, notes, user_id):
        self.name = name
        self.notes = notes
        self.user_id = user_id

    def __repr__(self):
        return '<id {}>'.format(self.id)
@dataclass
class Oslist(db.Model): # 제공 os
    __tablename__ = 'oslist'
    id: int
    os_name: str
    aws_image_id: str

    id = db.Column(db.Integer, primary_key=True)
    os_name = db.Column(db.String(30), nullable=False)
    aws_image_id = db.Column(db.String(30), nullable=False)

    def __json__(self):
        return ['id', 'os_name', 'aws_image_id']


    def __init__(self, os_name,aws_image_id ): 
        self.os_name = os_name
        self.aws_image_id = aws_image_id
    @property
    def serialize(self):
        return {
            'id': self.id,
            'os_name': self.os_name,
            'aws_image_id': self.aws_image_id,
        }

def dump_datetime(value):
    """Deserialize datetime object into string form for JSON processing."""
    if value is None:
        return None
    return [value.strftime("%Y-%m-%d"), value.strftime("%H:%M:%S")]

@dataclass
class Plan(db.Model):
    __tablename__ = 'plan'
    id: int
    plan_name: str
    aws_plan: str
    core: int
    ram: int
    traffic:int
    ssd: int
    iops: int

    id = db.Column(db.Integer, primary_key=True)
    plan_name = db.Column(db.String(30), nullable=False)
    aws_plan = db.Column(db.String(30), nullable=False)
    core = db.Column(db.Integer, nullable=False)
    ram = db.Column(db.Integer, nullable=False)
    traffic = db.Column(db.Integer, nullable=False)
    ssd = db.Column(db.Integer, nullable=False)
    iops = db.Column(db.Integer, nullable=False)
    def __json__(self):
        return ['id', 'plan_name', 'aws_plan', 'core', 'ram', 
        'traffic', 'ssd', 'iops']

    def __init__(self, plan_name, aws_plan, core, ram, traffic, ssd, iops):
        self.plan_name = plan_name
        self.aws_plan = aws_plan
        self.core = core
        self.ram = ram
        self.traffic = traffic 
        self.ssd = ssd
        self.iops = iops
    
    
    @property
    def serialize(self):
       """Return object data in easily serializable format"""
       return {
            'id': self.id,
            'plan_name': self.plan_name,
            'aws_plan': self.aws_plan,
            'core': self.core,
            'ram': self.ram,
            'traffic': self.traffic,
            'ssd': self.ssd,
            'iops': self.iops, 
        }
            
        

class VPC(db.Model):
    __tablename__ = 'user_vpc'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    vpc_id = db.Column(db.String(40), nullable=False)
    inter_gw_id = db.Column(db.String(40), nullable=False)
    default_subnet_id = db.Column(db.String(40), nullable=False)
    default_sec_id = db.Column(db.String(40), nullable=False)
    sub_subnet_id = db.Column(db.String(40), nullable=True) # other zone subnet for load banlanacer(app)

    secgroups = db.relationship('SecurityGroup', cascade = "all, delete", backref="VPC")
    subnets = db.relationship('Subnet', cascade = "all, delete", backref="VPC")
    
    def __init__(self, user_id, vpc_id, inter_gw_id, default_subnet_id, default_sec_id, sub_subnet_id):
        self.user_id = user_id
        self.vpc_id = vpc_id
        self.inter_gw_id = inter_gw_id
        self.default_subnet_id = default_subnet_id
        self.default_sec_id = default_sec_id
        self.sub_subnet_id = sub_subnet_id
        
    @property
    def as_dict(self):
       return {c.name: unicode(getattr(self, c.name)) for c in self.__table__.columns}

class NetInterface(db.Model):
    __tablename__ = 'netinterface'
    id = db.Column(db.Integer, primary_key=True)
    interface_id = db.Column(db.String(30), nullable=False)
    subnet_id = db.Column(db.Integer, db.ForeignKey("subnets.id"))
    cloud_id = db.Column(db.Integer, nullable=True) # cloud id
    attached_at = db.Column(db.DateTime, nullable=True)
    detached_at = db.Column(db.DateTime, nullable=True)
    deleted_at = db.Column(db.DateTime, nullable=True)

    def __init__(self, interface_id, subnet_id, cloud_id, attached_at=None): 
        self.cloud_id = cloud_id
        self.interface_id = interface_id
        self.subnet_id = subnet_id
        self.attached_at = attached_at
        
    @property
    def as_dict(self):
       return {c.name: unicode(getattr(self, c.name)) for c in self.__table__.columns}
        

class SecurityGroupAssociated(db.Model):
    __tablename__ = 'securitygroup_clouds'
    id = db.Column(db.Integer, primary_key=True)
    cloud_id = db.Column(db.Integer, nullable=False)
    sec_group_id = db.Column(db.Integer, nullable=False)

class SecurityGroup(db.Model):
    __tablename__ = 'securitygroup'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(30), nullable=False)
    sec_group_id = db.Column(db.String(30), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"))
    associated_to = db.Column(db.Integer, nullable=True) # cloud.id
    vpc_id = db.Column(db.Integer, db.ForeignKey("user_vpc.id"))
    
    secgroups = db.relationship('SecurityRule', cascade = "all, delete", backref="SecurityRule")
    
    def __init__(self, name, sec_group_id, user_id, associated_to, vpc_id):
        self.name = name
        self.sec_group_id = sec_group_id
        self.user_id = user_id
        self.associated_to = associated_to
        self.vpc_id = vpc_id

    @property
    def as_dict(self):
       return {c.name: unicode(getattr(self, c.name)) for c in self.__table__.columns}

class SecurityRule(db.Model):
    __tablename__ = 'securityrule'
    id = db.Column(db.Integer, primary_key=True) 
    protocol= db.Column(db.String(10), nullable=False)
    fromport = db.Column(db.Integer, nullable=False)
    toport = db.Column(db.Integer, nullable=False)
    cidr = db.Column(db.String(20), nullable=False)
    desc = db.Column(db.String(30), nullable=True)
    group_id = db.Column(db.Integer, db.ForeignKey("securitygroup.id"))
    
    def __init__(self, protocol, fromport, toport, cidr, desc, group_id):
        self.protocol = protocol
        self.fromport = fromport
        self.toport = toport
        self.cidr = cidr
        self.desc = desc
        self.group_id = group_id
        

@dataclass
class Subnet(db.Model):
    __tablename__ = 'subnets'
    id: int
    subnet_id: str
    cidr_block_ipv4: str 

    id = db.Column(db.Integer, primary_key=True)
    subnet_id = db.Column(db.String(30), nullable=False)
    cidr_block_ipv4 = db.Column(db.String(24))
    vpc_id = db.Column(db.Integer, db.ForeignKey('user_vpc.id'))
    

    def __init__(self, subnet_id, cidr_block_ipv4, vpc_id):
        self.subnet_id = subnet_id
        self.cidr_block_ipv4 = cidr_block_ipv4 
        self.vpc_id = vpc_id
        
    @property
    def as_dict(self):
       return {c.name: unicode(getattr(self, c.name)) for c in self.__table__.columns}
@dataclass
class Keypair(db.Model): #for connector
    __tablename__ = 'keypair'
    id: int
    name: str
    fingerprint: str
    keyid: str
    user_id: str
    keytoken: str

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(30), nullable=False)
    fingerprint = db.Column(db.String(59), nullable=True)
    keyid = db.Column(db.String(30), nullable=False)
    user_id = db.Column(db.Integer ,db.ForeignKey('users.id'), nullable=False)
    keytoken = db.Column(db.String(60), nullable=False) 

    def __init__(self, name, fingerprint, keyid, user_id, keytoken):
        self.name = name
        self.fingerprint = fingerprint
        self.keyid = keyid
        self.user_id = user_id
        self.keytoken = keytoken

    @property
    def as_dict(self):
       return {c.name: unicode(getattr(self, c.name)) for c in self.__table__.columns}

@dataclass
class Cloud(db.Model):
    __tablename__ = 'cloud'
    id: int
    hostname: str
    plan_id: int
    user_id: int
    os: str
    status: str
    ip_addr: str
    region: str
    created_at: str
    deleted_at: str
    keypair_id: str
    vpc_id: str
    aws_instance_id: str
    app_secret_access: str  
    is_lb_env_created: bool
    certificate_arn : str
    sec_group_id : int
    
    id = db.Column(db.Integer, primary_key=True)
    hostname = db.Column(db.String(30), nullable=False)
    plan_id = db.Column(db.Integer, db.ForeignKey('plan.id'))
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    os = db.Column(db.String(10), nullable=False)
    status = db.Column(db.String(15), nullable=False)
    ip_addr = db.Column(db.String(16), nullable=True) # IP할당이 늦어질 수 있기 때문에
    region = db.Column(db.String(10), nullable=False)
    created_at = db.Column(db.DateTime, nullable=True)
    deleted_at = db.Column(db.DateTime, nullable=True)
    keypair_id = db.Column(db.Integer, db.ForeignKey('keypair.id'))
    vpc_id = db.Column(db.Integer, db.ForeignKey('user_vpc.id'))
    aws_instance_id = db.Column(db.String(30), nullable=False)
    app_secret_access = db.Column(db.String(60), nullable=True) # access code .. 
    is_lb_env_created = db.Column(db.Boolean, nullable=True)
    certificate_arn = db.Column(db.String(100), nullable=True)
    sec_group_id = db.Column(db.Integer, db.ForeignKey('securitygroup.id'))
    targetgroup_arn = db.Column(db.String(100), nullable=True)
    loadbalancer_arn = db.Column(db.String(70), nullable=True)
    app_status = db.Column(db.String(6), nullable=True)
    def __json__(self):
        return ['id', 'hostname', 'plan_id', 'user_id', 'os', 
        'status', 'ip_addr', 'region', 'created_at', 'keypair_id',
        'vpc_id', 'aws_instance_id']

    def __init__(self, hostname, plan_id, user_id, os, status, ip_addr, region, keypair_id, vpc_id, aws_instance_id, app_secret_access,certificate_arn, sec_group_id):
        self.hostname = hostname
        self.plan_id = plan_id
        self.user_id = user_id
        self.os = os
        self.status = status
        self.ip_addr = ip_addr
        self.region = region
        self.created_at = datetime.datetime.now()
        self.keypair_id = keypair_id
        self.vpc_id = vpc_id
        self.aws_instance_id = aws_instance_id
        self.app_secret_access = app_secret_access
        self.is_lb_env_created = False 
        self.certificate_arn = ""
        self.sec_group_id = sec_group_id
        self.loadbalancer_arn=""
        self.targetgroup_arn= ""
        self.app_status = "blue"

    
    
    def as_dict(self):
       return {c.name: unicode(getattr(self, c.name)) for c in self.__table__.columns}


class Credit(db.Model):
    __tablename__ = 'credit'
    id = db.Column(db.Integer, primary_key=True)
    deposit_name = db.Column(db.Integer)
    bank = db.Column(db.String(12), nullable=False)
    charge_amount = db.Column(db.Integer, nullable=False)
    status = db.Column(db.Boolean, nullable=False, default=False)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    
    created_at = db.Column(db.DateTime, nullable=True)
    deleted_at = db.Column(db.DateTime, nullable=True)
    
    def __init__(self,deposit_name, bank, charge_amount, myid):
        self.deposit_name = deposit_name
        self.bank = bank
        self.charge_amount = charge_amount 
        self.status = False
        self.user_id = myid

class Balance(db.Model):
    __tablename__ = 'balance'
    id = db.Column(db.Integer, primary_key=True)
    balance = db.Column(db.Integer, nullable=False, default=0)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    
    def __init__(self, user_id):
        self.user_id = user_id

    
class Invoice(db.Model):
    __tablename__ = 'invoice'
    id = db.Column(db.Integer, primary_key=True)
    payment_amount = db.Column(db.Integer, nullable=False)
    status = db.Column(db.Boolean,nullable=False)
    
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    
class Support(db.Model):
    __tablename__ = 'support'
    id = db.Column(db.Integer, primary_key=True)
    support_type = db.Column(db.String(50), nullable=False)
    title = db.Column(db.String(100), primary_key=True)
    content = db.Column(db.Text, nullable=False)
    author_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    
    def __init__(self, support_type, title, content, author_id):
        self.support_type = support_type
        self.title = title
        self.content = content
        self.author_id = author_id


class ReplyTicket(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    reply_to = db.Column(db.Integer, db.ForeignKey('support.id'))
    content = db.Column(db.Text, nullable=False)
    author_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    
    def __init__(self, reply_to, content , author_id):
        self.reply_to = reply_to
        self.content = content
        self.author_id = author_id

class BlacklistToken(db.Model):
    """
    Token Model for storing JWT tokens
    """
    __tablename__ = 'blacklist_tokens'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    token = db.Column(db.String(500), unique=True, nullable=False)
    blacklisted_on = db.Column(db.DateTime, nullable=False)

    def __init__(self, token):
        self.token = token
        self.blacklisted_on = datetime.datetime.now()

    def __repr__(self):
        return '<id: token: {}'.format(self.token)


class SystemApi(db.Column):
    __tablename__ = 'systemapi'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    apiname = db.Column(db.String(20), nullable=False)
    version = db.Column(db.String(20), nullable=False)
    
    def __init__(self, apiname, version):
        self.apiname = apiname
        self.version = version
        
    
    
class AppVersions(db.Column):
    __tablename__ = 'apiupdate'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    app_id = db.Column(db.Integer, db.ForeignKey("apps.id"))
    version = db.Column(db.String)
    
    def __init__(self, app_id, version):
        self.app_id = app_id
        self.version = version
        
    
    
# class CloudApp(db.Model):
#     __tablename__ = "apps"
#     id = db.Column(db.Integer, primary_key=True, autoincrement=True)
#     name = db.Column(db.String(10), nullable=False)
#     image_source = db.Column(db.String(200), nullable=False) # Docker Image Id
#     bind_port = db.Column(db.Integer, nullable=False) # container's Port, main docker webserver must 80, 443

    
#     def __init__(self, name, image_source, bind_port, internal_api_version):
#         self.name = name
#         self.image_source = image_source
#         self.bind_port = bind_port # docker continaer port 
#         self.internal_api_version = internal_api_version
        

#         pass

# class CloudAppAssigned(db.Model):
#     __tablename__ = "cloudappassign"
#     id = db.Column(db.Integer, primary_key=True, autoincrement=True)
#     cloudid = db.Column(db.Integer, db.ForeignKey("cloud.id"))
#     appid = db.Column(db.Integer, db.ForeignKey("apps.id"))
#     lb_instance_id = db.Column(db.String(20), nullable=True)
#     blue_port = db.Column(db.Integer, default=8080)
#     green_port = db.Column(db.Integer, default=8081)
#     status = db.Column(db.String(10), nullable=True, default="blue") # green / blue status
#     created_at = db.Column(db.DateTime, nullable=True)
    
#     def __init__(self, cloudid, appid, lb_instance_id, blue_port=8080, green_port=8081):
#         self.cloudid = cloudid
#         self.appid = appid
#         self.lb_instance_id = lbInstance_id
#         self.blue_port = blue_port
#         self.green_port = green_port
#         self.created_at = datetime.datetime.now()
        
    

class CloudAppCommand(db.Model):
    __tablename__ = "appcommand"
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    action = db.Column(db.String(10), nullable=False) # deploy , update , rollback
    script = db.Column(db.Text, nullable=False)
    app_id = db.Column(db.Integer, db.ForeignKey('oslist.id'))
    sequence_num = db.Column(db.Integer, nullable=False)
    command_type = db.Column(db.String(10), nullable=True) # script / api , api -> somecloud  internal API 
    
    
    def __init__(self, action, script, app_id, sequence_num, command_type):
        self.action = action
        self.script = script
        self.app_id = app_id
        self.sequence_num = sequence_num
        self.command_type = command_type
        
# class AppVersions(db.Model):
#     __tablename__ = "appversions"
#     id = db.Column(db.Integer, primary_key=True, autoincrement=True)
#     appid = db.Column(db.Integer, db.ForeignKey("apps.id"))
#     version = db.Column(db.String(10), nullable=True)
#     def __init__(self, appid, version):
#         self.appid = appid
#         self.version = version
        
        
# class ChargeRequest(db.Model):
#     __tablename__= 'chargerequest'

# class Traffic(db.Model):
#     __tablename__ = 'traffic'
    


# class Invoice(db.Model):
#     __tablename__ = 'invoice'
