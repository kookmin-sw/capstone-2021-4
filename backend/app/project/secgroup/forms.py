from flask_wtf import FlaskForm
from wtforms import TextField, IntegerField
from wtforms.validators import DataRequired, Length


class SecGroupForm(FlaskForm):
    name = TextField('Name', validators=[DataRequired(),
                                         Length(min=1, max=254)])


class SecurityEditForm(FlaskForm):
    name = TextField('Name', validators=[DataRequired(),
                                         Length(min=1, max=254)])
    
    
class SecurityRuleEditForm(FlaskForm):
    fromport = IntegerField('fromport')
    toport = IntegerField('toport')
    protocol = TextField('protocol')
    cidr = TextField('cidr')

class SecurityRuleAddForm(FlaskForm):
    fromport = IntegerField('fromport')
    toport = IntegerField('toport')
    protocol = TextField('protocol')
    cidr = TextField('cidr')