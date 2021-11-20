from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager 
from flask_talisman import Talisman
from flask_seasurf import SeaSurf
from werkzeug.security import generate_password_hash
import os

db = SQLAlchemy()
talisman = Talisman()
    
def create_app():
    app = Flask(__name__)
    csrf = SeaSurf(app)
    
    csp = {'default-src':"'none'",'script-src': "'self'",'style-src':'https://stackpath.bootstrapcdn.com'}
    talisman.init_app(app,
        session_cookie_secure=False,
        force_https=False,
        content_security_policy=csp,
        frame_options='DENY')
    
    app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY')
    app.config['UPLOAD_FOLDER'] = os.path.abspath('app/uploads')
    app.config['MAX_CONTENT_LENGTH'] = 1 * 1024 * 1024  # 1 MB

    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///db/db.sqlite'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    app.config['SESSION_COOKIE_SAMESITE'] = "Strict"
    app.config['SESSION_COOKIE_HTTPONLY'] = True

    @app.cli.command("create-db")
    def create_db():
        db.create_all()
        from .models import User, File

        user = User(email=os.environ['EMAIL_FILESHARING'], password=generate_password_hash(os.environ['PASSWORD_FILESHARING'], method='sha256'))
        db.session.add(user)
        db.session.flush()
        db.session.refresh(user)

        note = File(user_id=user.id, uuid='ffffffffffffffffffffffffffffffff', filename='flag')
        db.session.add(note)
        db.session.commit()


    db.init_app(app)

    login_manager = LoginManager()
    login_manager.login_view = 'auth.login'
    login_manager.login_message = 'User needs to be logged in to view this page'
    login_manager.login_message_category = 'error'
    login_manager.init_app(app)

    from .models import User

    @login_manager.user_loader
    def load_user(user_id):
        # since the user_id is just the primary key of our user table, use it in the query for the user
        return User.query.get(int(user_id))

    # blueprint for auth routes in our app
    from .auth import auth as auth_blueprint
    app.register_blueprint(auth_blueprint)

    # blueprint for non-auth parts of app
    from .main import main as main_blueprint
    app.register_blueprint(main_blueprint)

    return app