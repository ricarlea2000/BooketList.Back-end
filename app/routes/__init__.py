from app.routes.auth import auth_bp
from app.routes.books import books_bp
from app.routes.library import library_bp
from app.routes.profile import profile_bp
from app.routes.health import health_bp
from app.routes.index import index_bp
from app.routes.users import users_bp 
from app.routes.admin import admin_bp

def register_blueprints(app):
    app.register_blueprint(auth_bp, url_prefix='/api/auth')
    app.register_blueprint(books_bp, url_prefix='/api')
    app.register_blueprint(library_bp, url_prefix='/api')
    app.register_blueprint(profile_bp, url_prefix='/api')
    app.register_blueprint(users_bp, url_prefix='/api')
    app.register_blueprint(admin_bp, url_prefix='/api/admin')
    app.register_blueprint(health_bp)
    app.register_blueprint(index_bp)