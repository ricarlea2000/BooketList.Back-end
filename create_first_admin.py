from app import create_app, db
from app.models import Admin

def create_first_admin():
    app = create_app()

    with app.app_context():
        if Admin.query.first():
            print("Ya existe un administrador en la base de datos")
            return
        
        admin = Admin(
            nombre_admin="Administrador Principal",
            email_admin="admin@booketlist.com",
            password_admin="admin123"
        )

        db.session.add(admin)
        db.session.commit()
        print("Administrador creado exitosamente")
        print(f"Email: admin@booketlist.com")
        print(f"Password: admin123")

if __name__ == '__main__':
    create_first_admin()