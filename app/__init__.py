from flask import Flask, url_for
from flask_sqlalchemy import SQLAlchemy
from flask_httpauth import HTTPBasicAuth
from flask_swagger_ui import get_swaggerui_blueprint
import os

db = SQLAlchemy()
auth = HTTPBasicAuth()

SWAGGER_URL = '/api/docs'
API_URL = '/static/swagger.json'

def create_app():
    '''
    Создает и настраивает Flask приложение.
    '''
    app = Flask(__name__, instance_relative_config=True, static_url_path='/static')

    app.config['SECRET_KEY'] = 'secret_key'
    app.config['SQLALCHEMY_DATABASE_URI'] = f"sqlite:///{os.path.join(app.instance_path, 'urls.db')}"
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False


    try:
        os.makedirs(app.instance_path)
    except OSError:
        pass

    static_dir = os.path.join(app.root_path, 'static')
    try:
        os.makedirs(static_dir)
    except OSError:
        pass

    db.init_app(app)

    swaggerui_blueprint = get_swaggerui_blueprint(
        SWAGGER_URL,
        API_URL,
        config={
            'app_name': "URL Alias API"
        }
    )
    app.register_blueprint(swaggerui_blueprint, url_prefix=SWAGGER_URL)


    from .routes import main_bp
    app.register_blueprint(main_bp)

    with app.app_context():
        from . import models
        db.create_all()

    return app 