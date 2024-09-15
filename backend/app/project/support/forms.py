from flask_wtf import FlaskForm
from wtforms import TextField
from wtforms.validators import DataRequired, Length


class AddTicketForm(FlaskForm):
    support_type = SelectField(u'지원 종류', choices=[('0', '기술 지원'), ('1', '요금 관련'), ('2', '기타')])
    title = TextField('title', validators=[DataRequired(),
                                         Length(min=1, max=254)])
    content = TextField('content')
    
    


class ReplyTicketForm(FlaskForm):
    content = TextField('content')
    # author_id, reply_to 는 back-end에서 제공.

