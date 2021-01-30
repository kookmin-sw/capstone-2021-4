from flask_wtf import FlaskForm
from wtforms import TextField, SelectField
from wtforms.validators import DataRequired, Length
from project.models import   Plan

class CloudForm(FlaskForm):
    Hostname = TextField('Hostname', validators=[DataRequired(),
                                         Length(min=1, max=254)])
    os = TextField('OS')
    plan = TextField('plan')
    subnet = TextField('subnet')
    keypair = TextField('keypair')


class EditCloudForm(FlaskForm):
    Hostname = TextField('Hostname', validators=[DataRequired(),
                                         Length(min=1, max=254)])
    
class PlanForm(FlaskForm):
    pass