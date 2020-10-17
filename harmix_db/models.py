import os
from flask_script import Manager
from flask_migrate import Migrate, MigrateCommand

from harmix_db.main_db import app, db

MIGRATION_DIR = os.path.join('migrations')

migrate = Migrate(app, db, directory=MIGRATION_DIR)
manager = Manager(app)

manager.add_command('db', MigrateCommand)


class Users(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    language = db.Column(db.String(50), unique=False, nullable=False)
    chat_id = db.Column(db.String(50), unique=False, nullable=True)
    subscription_term = db.Column(db.String(50), unique=False, nullable=True)
    user_id_code_web = db.Column(db.String(500), unique=False, nullable=True)
    last_function_before_pay = db.Column(db.String(50), unique=False, nullable=True)
    web_order_id = db.Column(db.String(100), unique=False, nullable=True)
    start_subscription_date = db.Column(db.String(50), unique=False, nullable=True)
    last_message_before_pay = db.Column(db.String(500), unique=False, nullable=True)
    buy_user_id_web = db.Column(db.String(500), unique=False, nullable=True)
    video_size_buttons = db.Column(db.String(10), unique=False, nullable=True)

    n_surveys = db.Column(db.Integer, unique=False, nullable=False)
    upload_response = db.Column(db.String(10000), unique=False, nullable=True)
    file_id = db.Column(db.String(1000), unique=False, nullable=True)

    file_size = db.Column(db.Integer, unique=False, nullable=True)
    get_url = db.Column(db.Integer, unique=False, nullable=False)
    message_id_buttons = db.Column(db.Integer, unique=False, nullable=False)
    n_answered_question = db.Column(db.Integer, unique=False, nullable=False)

    def __repr__(self):
        return '<Users - {};; {};; {};; {};; {};; {};; {}>'.format(self.id,
                                                                 self.language, self.chat_id,
                                                                 self.subscription_term,
                                                                 self.user_id_code_web)


class Survey(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    chat_id = db.Column(db.String(50), unique=False, nullable=True)
    question1 = db.Column(db.String(50), unique=False, nullable=True)
    question2 = db.Column(db.String(50), unique=False, nullable=True)
    question3 = db.Column(db.String(500), unique=False, nullable=True)
    question4 = db.Column(db.String(500), unique=False, nullable=True)

    def __repr__(self):
        return '<Survey - {};; {};; {};; {};; {};; {}>'.format(self.id, 
                                                                       self.question1, self.question2,
                                                                       self.question3, self.question4)


if __name__ == '__main__':
    manager.run()
