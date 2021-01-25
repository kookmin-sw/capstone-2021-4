from flask_wtf import FlaskForm
from wtforms import TextField
from wtforms.validators import DataRequired, Length


class CloudForm(FlaskForm):
    Hostname = TextField('Hostnme', validators=[DataRequired(),
                                         Length(min=1, max=254)])
    Plan = TextField('Plan')
    os = TextField('OS')


class EditCloudForm(FlaskForm):
    Hostname = TextField('Hostname', validators=[DataRequired(),
                                         Length(min=1, max=254)])
    
