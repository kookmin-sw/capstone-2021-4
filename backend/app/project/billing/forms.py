from flask_wtf import FlaskForm
from wtforms import TextField
from wtforms.validators import DataRequired, Length


class AddCredictForm(FlaskForm):
    deposit_name = TextField('deposit_name', validators=[DataRequired(),
                                         Length(min=1, max=254)])
    bank = TextField('bank')
    amount = TextField('amount')
    

