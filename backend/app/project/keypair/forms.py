from flask_wtf import FlaskForm
from wtforms import TextField, SelectField
from wtforms.validators import DataRequired, Length

class KeypairForm(FlaskForm):
    name = TextField('name', validators=[DataRequired(),
                                         Length(min=1, max=254)])


class EditKeypairForm(FlaskForm):
    keypairname = TextField('keypairname', validators=[DataRequired(),
                                         Length(min=1, max=254)])
     