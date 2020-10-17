from flask import Flask

from harmix_db.my_config import Config
from flask_sqlalchemy import SQLAlchemy

# create main app
app = Flask(__name__, template_folder="../web_server/templates",
            static_folder="../web_server/static")


# config for security in forms and other things
app.config.from_object(Config)

app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# connect data base
db = SQLAlchemy(app, session_options={

    'expire_on_commit': False

})
db.init_app(app)
# from app import app_site
# app.register_blueprint(app_site)
