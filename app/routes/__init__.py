from .auth import auth_bp
from .books import books_bp
from .library import library_bp
from .profile import profile_bp
from .health import health_bp
from .index import index_bp
from .users import users_bp 
from .admin import admin_bp

def register_blueprints(app):
    app.register_blueprint(auth_bp, url_prefix='/api/auth')
    app.register_blueprint(books_bp, url_prefix='/api')
    app.register_blueprint(library_bp, url_prefix='/api')
    app.register_blueprint(profile_bp, url_prefix='/api')
    app.register_blueprint(users_bp, url_prefix='/api')
    app.register_blueprint(admin_bp, url_prefix='/api/admin')
    app.register_blueprint(health_bp)
    app.register_blueprint(index_bp)