from project import db, bcrypt
from sqlalchemy.ext.hybrid import hybrid_property, hybrid_method
from datetime import datetime
from dataclasses import dataclass #Python 3.7+ and Flask 1.1+ https://stackoverflow.com/questions/5022066/how-to-serialize-sqlalchemy-result-to-json

