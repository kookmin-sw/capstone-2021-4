from project import app
from flask_oauthlib.client import OAuth

oauth = OAuth(app)
google = oauth.remote_app(
    'google',
    consumer_key=app.config.get('OAUTH_GOOGLE_CLIENTID'),
    consumer_secret=app.config.get('OAUTH_GOOGLE_SECRETKEY'),
    request_token_params={
        'scope': 'https://www.googleapis.com/auth/userinfo.email'
    },
    base_url='https://www.googleapis.com/oauth2/v1/',
    request_token_url=None,
    access_token_method='POST',
    access_token_url='https://accounts.google.com/o/oauth2/token',
    authorize_url='https://accounts.google.com/o/oauth2/auth',
)