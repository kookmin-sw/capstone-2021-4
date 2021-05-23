from flask_script import Manager, Server
# from flask_migrate import Migrate, MigrateCommand
import os

from app import app

# migrate = Migrate(app, db)
manager = Manager(app)

# manager.add_command('db', MigrateCommand)

if __name__ == '__main__':
    manager.add_command('runserver', Server(host='0.0.0.0', port=8001 ,   threaded=True))
    manager.run()