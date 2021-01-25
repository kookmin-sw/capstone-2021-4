from flask_script import Manager
from flask_migrate import Migrate, MigrateCommand
import os

from project import app, db
app.config.from_object(os.environ['APP_SETTINGS'])
print(os.environ['APP_SETTINGS'])
print("DB")
# print(SQLALCHEMY_DATABASE_URI)

migrate = Migrate(app, db)
manager = Manager(app)


manager.add_command('db', MigrateCommand)

if __name__ == '__main__':
    manager.run()