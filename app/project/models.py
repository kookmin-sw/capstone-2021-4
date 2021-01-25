from project import db, bcrypt
from sqlalchemy.ext.hybrid import hybrid_property, hybrid_method
from datetime import datetime


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
    items = db.relationship('Items', backref='user', lazy='dynamic')

    def __init__(self, email, password, email_confirmation_sent_on=None, role='user'):
        self.email = email
        self.password = password
        self.authenticated = False
        self.email_confirmation_sent_on = email_confirmation_sent_on
        self.email_confirmed = False
        self.email_confirmed_on = None
        self.registered_on = datetime.now()
        self.last_logged_in = None
        self.current_logged_in = datetime.now()
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

class Plan(db.Model):
    __tablename__ = 'plan'
    id = db.Column(db.Integer, primary_key=True)
    plan_name = db.Column(db.String(10), nullable=False)
    aws_plan = db.Column(db.String(10), nullable=False)
    core = db.Column(db.Integer, nullable=False)
    ram = db.Column(db.Integer, nullable=False)
    traffic = db.Column(db.Integer, nullable=False)
    ssd = db.Column(db.Integer, nullable=False)
    iops = db.Column(db.Integer, nullable=False)
    
    def __init__(self, plan_name, aws_plan, core, ram, traffic, ssd, iops):
        self.plan_name = plan_name
        self.aws_plan = aws_plan
        self.core = core
        self.ram = ram
        self.traffic = traffic 
        self.ssd = ssd
        self.iops = iops
        
 

class Cloud(db.Model):
    __tablename__ = 'cloud'
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
    
    def __init__(self, hostname, plan_id, user_id, os, status, ip_addr, region, created_at):
        self.hostname = hostname
        self.plan_id = plan_id
        self.user_id = user_id
        self.os = os
        self.status = status
        self.ip_addr = ip_addr
        self.region = region
        self.created_at = datetime.now()

# class Billing(db.Model):
#     __tablename__ = 'billing'

# class ChargeRequest(db.Model):
#     __tablename__= 'chargerequest'

# class Traffic(db.Model):
#     __tablename__ = 'traffic'
    
# class Support(db.Model):
#     __tablename__ = 'support'

# class Invoice(db.Model):
#     __tablename__ = 'invoice'
