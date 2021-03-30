import datetime
import os
import secrets

import pendulum
from project import app 
 

def now() -> pendulum.DateTime:
     
    return pendulum.now(tz=app.config["TZ"])


def datetime_to_pendulum(dt: datetime.datetime) -> pendulum.DateTime:
     
    return pendulum.instance(dt).in_tz(app.config["TZ"])

 