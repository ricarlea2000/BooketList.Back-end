# routes/admin.py
from flask import Blueprint, request, jsonify
from app.models import User, Book, Author, Rating, UserLibrary
from app import db
from app.errors import bad_request, not_found, internal_error, conflict, unauthorized
from sqlalchemy import func, and_

admin_bp = Blueprint('admin', __name__)

# ===== CREDENCIALES MAESTRAS DEL ADMIN (SOLO EN CÓDIGO) =====
ADMIN_MASTER_CREDENTIALS = {
    'username': 'booketadmin',
    'password': 'AdminBooket',
    'secret_key': 'BKTLST-ADM-2024-SECRET'
}

# ===== MIDDLEWARE DE VERIFICACIÓN DE ADMIN =====
def check_admin():
    """Verificar si la solicitud tiene las credenciales maestras de admin"""
    try:
        # Opción 1: Verificar header de autorización personalizado
        admin_secret = request.headers.get('X-Admin-Secret')
        if admin_secret and admin_secret == ADMIN_MASTER_CREDENTIALS['secret_key']:
            return None  # Autorizado
        
        # Opción 2: Verificar en el body de la solicitud
        data = request.get_json(silent=True) or {}
        admin_username = data.get('admin_username')
        admin_password = data.get('admin_password')
        
        if (admin_username and admin_password and 
            admin_username == ADMIN_MASTER_CREDENTIALS['username'] and 
            admin_password == ADMIN_MASTER_CREDENTIALS['password']):
            return None  # Autorizado
        
        # Opción 3: Verificar parámetros de query (para GET requests)
        admin_username = request.args.get('admin_username')
        admin_password = request.args.get('admin_password')
        
        if (admin_username and admin_password and 
            admin_username == ADMIN_MASTER_CREDENTIALS['username'] and 
            admin_password == ADMIN_MASTER_CREDENTIALS['password']):
            return None  # Autorizado
        
        return jsonify({
            "error": "No autorizado - Se requieren credenciales de administrador",
            "hint": "Usa X-Admin-Secret header o proporciona admin_username y admin_password"
        }), 403
        
    except Exception as e:
        return internal_error(str(e))

# ===== RUTA DE LOGIN PARA ADMIN =====
@admin_bp.route('/admin/login', methods=['POST'])
def admin_login():
    """Login para panel de administración con credenciales maestras"""
    try:
        data = request.get_json()
        
        if not data:
            return bad_request('Datos de login requeridos')
        
        username = data.get('username')
        password = data.get('password')
        
        if not username or not password:
            return bad_request('Username y password requeridos')
        
        if (username == ADMIN_MASTER_CREDENTIALS['username'] and 
            password == ADMIN_MASTER_CREDENTIALS['password']):
            
            return jsonify({
                'message': 'Login de administrador exitoso',
                'access_granted': True,
                'admin_user': ADMIN_MASTER_CREDENTIALS['username'],
                'secret_key': ADMIN_MASTER_CREDENTIALS['secret_key']
            }), 200
        else:
            return unauthorized('Credenciales de administrador inválidas')
    
    except Exception as e:
        return internal_error(str(e))

# ===== RUTAS DE USUARIOS =====
@admin_bp.route('/admin/users', methods=['GET'])
def get_all_users():
    """Obtener lista de todos los usuarios"""
    try:
        admin_check = check_admin()
        if admin_check:
            return admin_check
        
        users = User.query.all()
        return jsonify([user.serialize_public() for user in users]), 200
    
    except Exception as e:
        return internal_error(str(e))

@admin_bp.route('/admin/users/<int:user_id>', methods=['GET'])
def get_user(user_id):
    """Obtener información detallada de un usuario específico"""
    try:
        admin_check = check_admin()
        if admin_check:
            return admin_check
        
        user = User.query.get_or_404(user_id)
        return jsonify(user.serialize()), 200
    
    except Exception as e:
        return not_found(str(e))

@admin_bp.route('/admin/users/<int:user_id>/toggle-status', methods=['PUT'])
def toggle_user_status(user_id):
    """Alternar estado de usuario (bloquear/desbloquear)"""
    try:
        admin_check = check_admin()
        if admin_check:
            return admin_check
        
        user = User.query.get_or_404(user_id)
        user.is_active = not user.is_active
        db.session.commit()
        
        action = "desbloqueado" if user.is_active else "bloqueado"
        
        return jsonify({
            "message": f"Usuario {user.nombre_usuario} {user.apellido_usuario} {action} exitosamente",
            "user": user.serialize_public()
        }), 200
    
    except Exception as e:
        db.session.rollback()
        return internal_error(str(e))

@admin_bp.route('/admin/users/stats', methods=['GET'])
def get_users_stats():
    """Obtener estadísticas de usuarios"""
    try:
        admin_check = check_admin()
        if admin_check:
            return admin_check
        
        total_users = User.query.count()
        active_users = User.query.filter_by(is_active=True).count()
        blocked_users = User.query.filter_by(is_active=False).count()
        
        users_with_books = db.session.query(func.count(func.distinct(UserLibrary.id_usuario))).scalar()
        users_with_reviews = db.session.query(func.count(func.distinct(Rating.id_usuario))).scalar()
        
        return jsonify({
            "total_users": total_users,
            "active_users": active_users,
            "blocked_users": blocked_users,
            "users_with_books": users_with_books,
            "users_with_reviews": users_with_reviews,
            "active_percentage": round((active_users / total_users) * 100, 2) if total_users > 0 else 0
        }), 200
    
    except Exception as e:
        return internal_error(str(e))

# ===== RUTAS DE LIBROS =====
@admin_bp.route('/admin/books', methods=['GET'])
def get_all_books():
    """Obtener todos los libros con información completa"""
    try:
        admin_check = check_admin()
        if admin_check:
            return admin_check
        
        books = Book.query.all()
        return jsonify([{
            'id_libros': libro.id_libros,
            'titulo_libro': libro.titulo_libro,
            'autor': f"{libro.autor.nombre_autor} {libro.autor.apellido_autor}" if libro.autor else "Desconocido",
            'id_autor': libro.id_autor,
            'genero_libro': libro.genero_libro,
            'descripcion_libros': libro.descripcion_libros,
            'enlace_portada_libro': libro.enlace_portada_libro,
            'enlace_asin_libro': libro.enlace_asin_libro,
            'created_at': libro.created_at.isoformat() if libro.created_at else None,
            'total_resenas': len(libro.calificaciones),
            'rating_promedio': db.session.query(func.avg(Rating.calificacion)).filter(
                Rating.id_libro == libro.id_libros
            ).scalar() or 0
        } for libro in books]), 200
    
    except Exception as e:
        return internal_error(str(e))

@admin_bp.route('/admin/books/<int:book_id>', methods=['GET'])
def get_book_detail(book_id):
    """Obtener información detallada de un libro"""
    try:
        admin_check = check_admin()
        if admin_check:
            return admin_check
        
        libro = Book.query.get_or_404(book_id)
        
        total_reviews = len(libro.calificaciones)
        avg_rating = db.session.query(func.avg(Rating.calificacion)).filter(
            Rating.id_libro == book_id
        ).scalar() or 0
        in_libraries = UserLibrary.query.filter_by(id_libro=book_id).count()
        
        return jsonify({
            'book': libro.serialize(),
            'stats': {
                'total_reviews': total_reviews,
                'average_rating': round(float(avg_rating), 2),
                'in_user_libraries': in_libraries,
                'total_users_rated': total_reviews
            }
        }), 200
    
    except Exception as e:
        return not_found(str(e))

@admin_bp.route('/admin/books/create', methods=['POST'])
def create_book():
    """Crear un nuevo libro"""
    try:
        admin_check = check_admin()
        if admin_check:
            return admin_check
        
        data = request.get_json()
        
        required_fields = ['titulo_libro', 'id_autor', 'genero_libro', 'descripcion_libros']
        for field in required_fields:
            if not data.get(field):
                return bad_request(f'Campo {field} es requerido')
        
        author = Author.query.get(data['id_autor'])
        if not author:
            return not_found('Autor no encontrado')
        
        libro = Book(
            titulo_libro=data['titulo_libro'],
            id_autor=data['id_autor'],
            genero_libro=data['genero_libro'],
            descripcion_libros=data['descripcion_libros'],
            enlace_portada_libro=data.get('enlace_portada_libro', ''),
            enlace_asin_libro=data.get('enlace_asin_libro', '')
        )
        
        db.session.add(libro)
        db.session.commit()
        
        return jsonify({
            'message': 'Libro creado exitosamente',
            'book': libro.serialize()
        }), 201
    
    except Exception as e:
        db.session.rollback()
        return internal_error(str(e))

@admin_bp.route('/admin/books/update/<int:book_id>', methods=['PUT'])
def update_book(book_id):
    """Actualizar información de un libro"""
    try:
        admin_check = check_admin()
        if admin_check:
            return admin_check
        
        libro = Book.query.get_or_404(book_id)
        data = request.get_json()
        
        updatable_fields = ['titulo_libro', 'id_autor', 'genero_libro', 'descripcion_libros', 
                           'enlace_portada_libro', 'enlace_asin_libro']
        
        for field in updatable_fields:
            if field in data:
                setattr(libro, field, data[field])
        
        db.session.commit()
        
        return jsonify({
            'message': 'Libro actualizado exitosamente',
            'book': libro.serialize()
        }), 200
    
    except Exception as e:
        db.session.rollback()
        return internal_error(str(e))

@admin_bp.route('/admin/books/delete/<int:book_id>', methods=['DELETE'])
def delete_book(book_id):
    """Eliminar un libro"""
    try:
        admin_check = check_admin()
        if admin_check:
            return admin_check
        
        libro = Book.query.get_or_404(book_id)
        
        has_reviews = Rating.query.filter_by(id_libro=book_id).first()
        in_libraries = UserLibrary.query.filter_by(id_libro=book_id).first()
        
        if has_reviews or in_libraries:
            return bad_request('No se puede eliminar el libro porque tiene reseñas o está en bibliotecas de usuarios')
        
        db.session.delete(libro)
        db.session.commit()
        
        return jsonify({
            'message': 'Libro eliminado exitosamente'
        }), 200
    
    except Exception as e:
        db.session.rollback()
        return internal_error(str(e))

# ===== RUTAS DE AUTORES =====
@admin_bp.route('/admin/authors', methods=['GET'])
def get_all_authors():
    """Obtener todos los autores"""
    try:
        admin_check = check_admin()
        if admin_check:
            return admin_check
        
        authors = Author.query.all()
        return jsonify([{
            'id_autor': autor.id_autor,
            'nombre_autor': autor.nombre_autor,
            'apellido_autor': autor.apellido_autor,
            'nombre_completo': f"{autor.nombre_autor} {autor.apellido_autor}",
            'biografia_autor': autor.biografia_autor,
            'total_libros': len(autor.libros),
            'created_at': autor.created_at.isoformat() if autor.created_at else None
        } for autor in authors]), 200
    
    except Exception as e:
        return internal_error(str(e))

@admin_bp.route('/admin/authors/<int:author_id>', methods=['GET'])
def get_author_detail(author_id):
    """Obtener información detallada de un autor"""
    try:
        admin_check = check_admin()
        if admin_check:
            return admin_check
        
        author = Author.query.get_or_404(author_id)
        author_books = Book.query.filter_by(id_autor=author_id).all()
        
        return jsonify({
            'author': author.serialize(),
            'books': [book.serialize() for book in author_books],
            'stats': {
                'total_books': len(author_books),
                'genres': list(set([book.genero_libro for book in author_books])),
                'first_book_date': min([book.created_at for book in author_books]).isoformat() if author_books else None
            }
        }), 200
    
    except Exception as e:
        return not_found(str(e))

@admin_bp.route('/admin/authors/create', methods=['POST'])
def create_author():
    """Crear un nuevo autor"""
    try:
        admin_check = check_admin()
        if admin_check:
            return admin_check
        
        data = request.get_json()
        
        if not data.get('nombre_autor') or not data.get('apellido_autor'):
            return bad_request('Nombre y apellido del autor son requeridos')
        
        autor = Author(
            nombre_autor=data['nombre_autor'],
            apellido_autor=data['apellido_autor'],
            biografia_autor=data.get('biografia_autor', '')
        )
        
        db.session.add(autor)
        db.session.commit()
        
        return jsonify({
            'message': 'Autor creado exitosamente',
            'author': autor.serialize()
        }), 201
    
    except Exception as e:
        db.session.rollback()
        return internal_error(str(e))
@admin_bp.route('/admin/authors/update/<int:author_id>', methods=['PUT'])
def update_author(author_id):
    """Actualizar información de un autor"""
    try:
        admin_check = check_admin()
        if admin_check:
            return admin_check
        
        author = Author.query.get_or_404(author_id)
        data = request.get_json()
        
        # Campos actualizables
        if 'nombre_autor' in data:
            author.nombre_autor = data['nombre_autor']
        
        if 'apellido_autor' in data:
            author.apellido_autor = data['apellido_autor']
        
        if 'biografia_autor' in data:
            author.biografia_autor = data['biografia_autor']
        
        db.session.commit()
        
        return jsonify({
            'message': 'Autor actualizado exitosamente',
            'author': author.serialize()
        }), 200
    
    except Exception as e:
        db.session.rollback()
        return internal_error(str(e))
    
@admin_bp.route('/admin/authors/delete/<int:author_id>', methods=['DELETE'])
def delete_author(author_id):
    """Eliminar un autor y todos sus libros (con verificación de dependencias)"""
    try:
        admin_check = check_admin()
        if admin_check:
            return admin_check
        
        author = Author.query.get_or_404(author_id)
        
        # Verificar si el autor tiene libros
        author_books = Book.query.filter_by(id_autor=author_id).all()
        
        # Verificar dependencias antes de eliminar
        books_with_dependencies = []
        
        for book in author_books:
            # Verificar si el libro tiene reseñas
            has_reviews = Rating.query.filter_by(id_libro=book.id_libros).first()
            # Verificar si el libro está en bibliotecas de usuarios
            in_libraries = UserLibrary.query.filter_by(id_libro=book.id_libros).first()
            
            if has_reviews or in_libraries:
                books_with_dependencies.append({
                    'id_libros': book.id_libros,
                    'titulo_libro': book.titulo_libro,
                    'tiene_resenas': has_reviews is not None,
                    'en_bibliotecas': in_libraries is not None
                })
        
        # Si hay libros con dependencias, no podemos eliminar
        if books_with_dependencies:
            return jsonify({
                "error": "No se puede eliminar el autor porque algunos libros tienen dependencias",
                "libros_con_dependencias": books_with_dependencies,
                "total_libros_con_problemas": len(books_with_dependencies),
                "sugerencia": "Elimina primero las reseñas y quita los libros de las bibliotecas de usuarios"
            }), 409
        
        # Si no hay dependencias, proceder con la eliminación
        # Primero eliminar todos los libros del autor
        for book in author_books:
            db.session.delete(book)
        
        # Luego eliminar el autor
        db.session.delete(author)
        db.session.commit()
        
        return jsonify({
            'message': f'Autor "{author.nombre_autor} {author.apellido_autor}" y {len(author_books)} libros eliminados exitosamente',
            'autor_eliminado': author.serialize(),
            'total_libros_eliminados': len(author_books)
        }), 200
    
    except Exception as e:
        db.session.rollback()
        return internal_error(str(e))

@admin_bp.route('/admin/authors/delete-force/<int:author_id>', methods=['DELETE'])
def force_delete_author(author_id):
    """ELIMINACIÓN FORZADA: Eliminar autor y todos sus libros (incluyendo dependencias)"""
    try:
        admin_check = check_admin()
        if admin_check:
            return admin_check
        
        author = Author.query.get_or_404(author_id)
        author_books = Book.query.filter_by(id_autor=author_id).all()
        
        # Estadísticas antes de eliminar
        total_libros = len(author_books)
        total_resenas = 0
        total_en_bibliotecas = 0
        
        # Eliminar dependencias primero
        for book in author_books:
            # Eliminar reseñas de este libro
            reviews_deleted = Rating.query.filter_by(id_libro=book.id_libros).delete()
            total_resenas += reviews_deleted
            
            # Eliminar de bibliotecas de usuarios
            libraries_deleted = UserLibrary.query.filter_by(id_libro=book.id_libros).delete()
            total_en_bibliotecas += libraries_deleted
            
            # Eliminar el libro
            db.session.delete(book)
        
        # Eliminar el autor
        db.session.delete(author)
        db.session.commit()
        
        return jsonify({
            'message': f'ELIMINACIÓN COMPLETA: Autor y todos sus datos eliminados',
            'autor_eliminado': f"{author.nombre_autor} {author.apellido_autor}",
            'estadisticas': {
                'total_libros_eliminados': total_libros,
                'total_resenas_eliminadas': total_resenas,
                'total_bibliotecas_limpiadas': total_en_bibliotecas
            },
            'advertencia': 'Esta acción no se puede deshacer'
        }), 200
    
    except Exception as e:
        db.session.rollback()
        return internal_error(str(e))

# ===== DASHBOARD ESTADÍSTICAS GENERALES =====
@admin_bp.route('/admin/dashboard/stats', methods=['GET'])
def get_dashboard_stats():
    """Obtener estadísticas generales para el dashboard de administración"""
    try:
        admin_check = check_admin()
        if admin_check:
            return admin_check
        
        total_users = User.query.count()
        total_books = Book.query.count()
        total_authors = Author.query.count()
        total_reviews = Rating.query.count()
        
        active_users = User.query.filter_by(is_active=True).count()
        blocked_users = User.query.filter_by(is_active=False).count()
        
        return jsonify({
            "totals": {
                "total_users": total_users,
                "total_books": total_books,
                "total_authors": total_authors,
                "total_reviews": total_reviews,
                "active_users": active_users,
                "blocked_users": blocked_users
            }
        }), 200
    
    except Exception as e:
        return internal_error(str(e))

# ===== RUTA PARA VERIFICAR CREDENCIALES =====
@admin_bp.route('/admin/verify', methods=['POST'])
def verify_admin():
    """Verificar si las credenciales de admin son válidas"""
    try:
        data = request.get_json()
        
        if not data:
            return bad_request('Datos requeridos')
        
        username = data.get('username')
        password = data.get('password')
        
        if (username == ADMIN_MASTER_CREDENTIALS['username'] and 
            password == ADMIN_MASTER_CREDENTIALS['password']):
            
            return jsonify({
                'valid': True,
                'message': 'Credenciales válidas',
                'secret_key': ADMIN_MASTER_CREDENTIALS['secret_key']
            }), 200
        else:
            return jsonify({
                'valid': False,
                'message': 'Credenciales inválidas'
            }), 401
    
    except Exception as e:
        return internal_error(str(e))