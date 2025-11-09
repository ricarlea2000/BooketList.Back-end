from flask import Blueprint, request, jsonify
from app.models import Admin, Author, Book, User, Rating, UserLibrary
from app import db
from app.errors import bad_request, unauthorized, conflict, internal_error, not_found
from flask_jwt_extended import create_access_token, jwt_required, get_jwt_identity
from sqlalchemy import func

admin_bp = Blueprint('admin', __name__)

# ===== AUTHENTICATION =====
@admin_bp.route('/admin/auth/register', methods=['POST'])
def admin_register_user():
    """Registrar un nuevo administrador"""
    try:
        data = request.get_json()

        if not data:
            return bad_request('Datos de registro requeridos')

        required_fields = ['nombre_admin', 'email_admin', 'password_admin']
        for field in required_fields:
            if not data.get(field):
                return bad_request(f'El campo {field} es requerido')

        existing_admin = Admin.query.filter_by(email_admin=data['email_admin']).first()
        if existing_admin:
            return conflict('El correo electrónico ya está registrado')

        admin = Admin(
            nombre_admin=data['nombre_admin'],
            email_admin=data['email_admin'],
            password_admin=data['password_admin']
        )

        if 'is_active' in data:
            admin.is_active = data['is_active']

        db.session.add(admin)
        db.session.commit()

        access_token = create_access_token(
            identity=str(admin.id_admin),
            additional_claims={'is_admin': True}
        )

        return jsonify({
            'message': 'Administrador registrado exitosamente',
            'access_token': access_token,
            'admin': admin.serialize()
        }), 201

    except Exception as e:
        db.session.rollback()
        return internal_error(str(e))

@admin_bp.route('/admin/login', methods=['POST'])
def admin_login_user():
    """Login para administradores"""
    try:
        data = request.get_json()
        email = data.get('email_admin')
        password = data.get('password_admin')

        if not email or not password:
            return bad_request('Correo electrónico y contraseña requeridos')
        
        admin = Admin.query.filter_by(email_admin=email).first()

        if not admin:
            return unauthorized('Credenciales inválidas')
        
        if not admin.is_active:
            return unauthorized('Cuenta de administrador desactivada')
        
        if not admin.check_password(password):
            return unauthorized('Credenciales inválidas')
        
        access_token = create_access_token(
            identity=str(admin.id_admin),
            additional_claims={'is_admin': True}
        )

        return jsonify({
            'message': 'Ingreso de administrador exitoso',
            'access_token': access_token,
            'admin': admin.serialize()
        }), 200
    
    except Exception as e:
        return internal_error(str(e))

@admin_bp.route('/admin/profile', methods=['GET'])
@jwt_required()
def admin_get_profile():
    """Obtener perfil del administrador"""
    try:
        current_admin_id = get_jwt_identity()
        admin = Admin.query.get(current_admin_id)

        if not admin:
            return not_found('Administrador no encontrado')
        
        return jsonify(admin.serialize()), 200
    
    except Exception as e:
        return internal_error(str(e))

@admin_bp.route('/admin/auth/profile', methods=['PUT'])
@jwt_required()
def admin_update_profile():
    """Actualizar perfil del administrador"""
    try:
        current_admin_id = get_jwt_identity()
        admin = Admin.query.get(current_admin_id)

        if not admin:
            return not_found('Administrador no encontrado')
        
        data = request.get_json()

        if 'nombre_admin' in data:
            admin.nombre_admin = data['nombre_admin']
        
        if 'email_admin' in data:
            existing_admin = Admin.query.filter(
                Admin.email_admin == data['email_admin'],
                Admin.id_admin != current_admin_id
            ).first()
            if existing_admin:
                return conflict('El correo electrónico ya está en uso')
            admin.email_admin = data['email_admin']

        if 'password_admin' in data and data['password_admin']:
            admin.set_password(data['password_admin'])
        
        db.session.commit()

        return jsonify({
            'message': 'Perfil actualizado exitosamente',
            'admin': admin.serialize()
        }), 200
    
    except Exception as e:
        db.session.rollback()
        return internal_error(str(e))

# ===== USER MANAGEMENT =====
@admin_bp.route('/admin/users/all', methods=['GET'])
@jwt_required()
def admin_get_all_users():
    """Obtener todos los usuarios"""
    try:
        current_admin_id = get_jwt_identity()
        current_admin = Admin.query.get(current_admin_id)

        if not current_admin:
            return unauthorized('No tiene permiso para ver usuarios')
        
        users = User.query.all()
        # ✅ CORREGIR: Usar serialize() en lugar de serialize_admin()
        return jsonify([user.serialize() for user in users]), 200
    
    except Exception as e:
        return internal_error(str(e))

@admin_bp.route('/admin/users/<int:user_id>', methods=['GET'])
@jwt_required()
def admin_get_user_detail(user_id):  # <- Agregar user_id aquí
    """Obtener detalles de un usuario específico"""
    try:
        current_admin_id = get_jwt_identity()
        current_admin = Admin.query.get(current_admin_id)

        if not current_admin:
            return unauthorized('No tiene permiso para ver usuarios')
        
        user = User.query.get_or_404(user_id)
        return jsonify(user.serialize()), 200
    
    except Exception as e:
        return not_found(str(e))

@admin_bp.route('/admin/users/<int:user_id>/status', methods=['PUT'])
@jwt_required()
def admin_toggle_user_status(user_id):  # <- Agregar user_id aquí
    """Cambiar estado de usuario (bloquear/desbloquear)"""
    try:
        current_admin_id = get_jwt_identity()
        current_admin = Admin.query.get(current_admin_id)

        if not current_admin:
            return unauthorized('No tiene permiso para gestionar usuarios')
        
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
    except Exception as e:
        db.session.rollback()
        return internal_error(str(e))

@admin_bp.route('/admin/users/<int:user_id>/reviews', methods=['GET'])
@jwt_required()
def admin_get_user_reviews(user_id):
    """Obtener todas las reseñas de un usuario específico"""
    try:
        current_admin_id = get_jwt_identity()
        current_admin = Admin.query.get(current_admin_id)

        if not current_admin:
            return unauthorized('No tiene permiso para ver reseñas de usuarios')
        
        user = User.query.get_or_404(user_id)
        
        reviews = Rating.query.filter_by(id_usuario=user_id).all()
        
        reviews_data = []
        for review in reviews:
            book = Book.query.get(review.id_libro)
            reviews_data.append({
                'id_calificacion': review.id_calificacion,
                'book': {
                    'id_libros': book.id_libros if book else None,
                    'titulo_libro': book.titulo_libro if book else 'Libro no encontrado',
                    'autor': f"{book.autor.nombre_autor} {book.autor.apellido_autor}" if book and book.autor else 'Autor desconocido',
                    'enlace_portada_libro': book.enlace_portada_libro if book else None
                },
                'calificacion': review.calificacion,
                'resena': review.resena,
                'created_at': review.created_at.isoformat() if review.created_at else None,
                'updated_at': review.updated_at.isoformat() if review.updated_at else None
            })
        
        return jsonify({
            'user_id': user_id,
            'user_name': f"{user.nombre_usuario} {user.apellido_usuario}",
            'total_reviews': len(reviews_data),
            'reviews': reviews_data
        }), 200
    
    except Exception as e:
        return internal_error(str(e))

@admin_bp.route('/admin/users/<int:user_id>/library', methods=['GET'])
@jwt_required()
def admin_get_user_library(user_id):
    """Obtener toda la biblioteca de un usuario específico (incluyendo libros leídos)"""
    try:
        current_admin_id = get_jwt_identity()
        current_admin = Admin.query.get(current_admin_id)

        if not current_admin:
            return unauthorized('No tiene permiso para ver bibliotecas de usuarios')
        
        user = User.query.get_or_404(user_id)
        
        # ✅ Obtener libros de UserLibrary (quiero_leer y leyendo)
        library_items = UserLibrary.query.filter_by(id_usuario=user_id).all()
        
        # ✅ Obtener libros leídos de Rating
        read_books = Rating.query.filter_by(id_usuario=user_id).all()
        
        library_data = []
        
        # Procesar libros de UserLibrary
        for item in library_items:
            book = Book.query.get(item.id_libro)
            if book:
                library_data.append({
                    'id_biblioteca': item.id_biblioteca,
                    'book': {
                        'id_libros': book.id_libros,
                        'titulo_libro': book.titulo_libro,
                        'autor': f"{book.autor.nombre_autor} {book.autor.apellido_autor}" if book.autor else 'Autor desconocido',
                        'genero_libro': book.genero_libro,
                        'enlace_portada_libro': book.enlace_portada_libro
                    },
                    'estado_lectura': item.estado_lectura,
                    'added_at': item.created_at.isoformat() if item.created_at else None,
                    'source': 'user_library'  # Para identificar de dónde viene
                })
        
        # Procesar libros leídos de Rating
        for rating in read_books:
            book = Book.query.get(rating.id_libro)
            if book:
                library_data.append({
                    'id_calificacion': rating.id_calificacion,
                    'book': {
                        'id_libros': book.id_libros,
                        'titulo_libro': book.titulo_libro,
                        'autor': f"{book.autor.nombre_autor} {book.autor.apellido_autor}" if book.autor else 'Autor desconocido',
                        'genero_libro': book.genero_libro,
                        'enlace_portada_libro': book.enlace_portada_libro
                    },
                    'estado_lectura': 'leido',
                    'calificacion': rating.calificacion,
                    'resena': rating.resena,
                    'added_at': rating.created_at.isoformat() if rating.created_at else None,
                    'source': 'rating'  # Para identificar de dónde viene
                })
        
        # Estadísticas por estado de lectura (ahora incluye libros leídos)
        stats = {
            'total_books': len(library_data),
            'quiero_leer': len([item for item in library_data if item['estado_lectura'] == 'quiero_leer']),
            'leyendo': len([item for item in library_data if item['estado_lectura'] == 'leyendo']),
            'leido': len([item for item in library_data if item['estado_lectura'] == 'leido'])
        }
        
        return jsonify({
            'user_id': user_id,
            'user_name': f"{user.nombre_usuario} {user.apellido_usuario}",
            'stats': stats,
            'library': library_data
        }), 200
    
    except Exception as e:
        return internal_error(str(e))

@admin_bp.route('/admin/users/<int:user_id>/stats', methods=['GET'])
@jwt_required()
def admin_get_user_stats(user_id):
    """Obtener estadísticas completas de un usuario (incluyendo libros leídos)"""
    try:
        current_admin_id = get_jwt_identity()
        current_admin = Admin.query.get(current_admin_id)

        if not current_admin:
            return unauthorized('No tiene permiso para ver estadísticas de usuarios')
        
        user = User.query.get_or_404(user_id)
        
        # Contar reseñas
        total_reviews = Rating.query.filter_by(id_usuario=user_id).count()
        
        # ✅ Contar libros en UserLibrary por estado
        library_stats = db.session.query(
            UserLibrary.estado_lectura,
            func.count(UserLibrary.id_biblioteca).label('count')
        ).filter_by(id_usuario=user_id).group_by(UserLibrary.estado_lectura).all()
        
        # ✅ Contar libros leídos en Rating
        read_books_count = Rating.query.filter_by(id_usuario=user_id).count()
        
        stats_dict = {'quiero_leer': 0, 'leyendo': 0, 'leido': read_books_count}
        
        # Sumar los libros de UserLibrary
        for estado, count in library_stats:
            stats_dict[estado] = count
        
        total_books = sum(stats_dict.values())
        
        # ✅ Obtener información adicional sobre reseñas
        reviews_with_rating = Rating.query.filter(
            Rating.id_usuario == user_id,
            Rating.calificacion.isnot(None)
        ).count()
        
        reviews_with_text = Rating.query.filter(
            Rating.id_usuario == user_id,
            Rating.resena.isnot(None),
            Rating.resena != ''
        ).count()
        
        return jsonify({
            'user_id': user_id,
            'user_name': f"{user.nombre_usuario} {user.apellido_usuario}",
            'stats': {
                'total_books': total_books,
                'total_reviews': total_reviews,
                'reading_status': stats_dict,
                'reviews_detail': {
                    'with_rating': reviews_with_rating,
                    'with_text': reviews_with_text,
                    'without_rating': total_reviews - reviews_with_rating
                }
            }
        }), 200
    
    except Exception as e:
        return internal_error(str(e))

# ===== AUTHOR MANAGEMENT =====
@admin_bp.route('/admin/authors/create', methods=['POST'])
@jwt_required()
def admin_create_author():
    """Crear un nuevo autor"""
    try:
        current_admin_id = get_jwt_identity()
        current_admin = Admin.query.get(current_admin_id)

        if not current_admin:
            return unauthorized('No tiene permiso para agregar autores')
        
        data = request.get_json()

        if not data.get('nombre_autor') or not data.get('apellido_autor'):
            return bad_request('Nombre y apellido del autor son requeridos')
        
        existing_author = Author.query.filter_by(
            nombre_autor=data['nombre_autor'],
            apellido_autor=data['apellido_autor']
        ).first()

        if existing_author:
            return conflict('El autor ya existe en la base de datos')
        
        # Crear autor sin el campo imagen_autor por ahora
        author = Author(
            nombre_autor=data['nombre_autor'],
            apellido_autor=data['apellido_autor'],
            biografia_autor=data.get('biografia_autor', '')
            # No incluir imagen_autor temporalmente
        )

        db.session.add(author)
        db.session.commit()

        return jsonify({
            'message': 'Autor agregado exitosamente',
            'author': {
                'id_autor': author.id_autor,
                'nombre_autor': author.nombre_autor,
                'apellido_autor': author.apellido_autor,
                'biografia_autor': author.biografia_autor,
                'created_at': author.created_at.isoformat() if author.created_at else None,
                'updated_at': author.updated_at.isoformat() if author.updated_at else None
            }
        }), 201
    
    except Exception as e:
        db.session.rollback()
        return internal_error(str(e))

@admin_bp.route('/admin/authors/list', methods=['GET'])
@jwt_required()
def admin_get_all_authors():
    """Obtener lista de todos los autores"""
    try:
        current_admin_id = get_jwt_identity()
        current_admin = Admin.query.get(current_admin_id)

        if not current_admin:
            return unauthorized('No tiene permiso para ver autores')
        
        # Usar consulta específica para evitar el campo problemático
        authors = db.session.query(
            Author.id_autor,
            Author.nombre_autor,
            Author.apellido_autor,
            Author.biografia_autor,
            Author.created_at,
            Author.updated_at
        ).all()
        
        authors_data = []
        for author in authors:
            authors_data.append({
                'id_autor': author.id_autor,
                'nombre_autor': author.nombre_autor,
                'apellido_autor': author.apellido_autor,
                'biografia_autor': author.biografia_autor,
                'imagen_autor': None,  # Valor por defecto
                'created_at': author.created_at.isoformat() if author.created_at else None,
                'updated_at': author.updated_at.isoformat() if author.updated_at else None
            })
        
        return jsonify(authors_data), 200
    
    except Exception as e:
        return internal_error(str(e))

@admin_bp.route('/admin/authors/<int:author_id>/update', methods=['PUT'])
@jwt_required()
def admin_update_author(author_id):
    """Actualizar información de un autor"""
    try:
        current_admin_id = get_jwt_identity()
        current_admin = Admin.query.get(current_admin_id)

        if not current_admin:
            return unauthorized('No tiene permiso para actualizar autores')
        
        author = Author.query.get_or_404(author_id)
        data = request.get_json()

        if 'nombre_autor' in data:
            author.nombre_autor = data['nombre_autor']
        if 'apellido_autor' in data:
            author.apellido_autor = data['apellido_autor']
        if 'biografia_autor' in data:
            author.biografia_autor = data['biografia_autor']
        # No actualizar imagen_autor por ahora
        
        db.session.commit()

        return jsonify({
            'message': 'Autor actualizado exitosamente',
            'author': {
                'id_autor': author.id_autor,
                'nombre_autor': author.nombre_autor,
                'apellido_autor': author.apellido_autor,
                'biografia_autor': author.biografia_autor,
                'imagen_autor': None,
                'created_at': author.created_at.isoformat() if author.created_at else None,
                'updated_at': author.updated_at.isoformat() if author.updated_at else None
            }
        }), 200
    
    except Exception as e:
        db.session.rollback()
        return internal_error(str(e))

@admin_bp.route('/admin/authors/<int:author_id>/delete', methods=['DELETE'])
@jwt_required()
def admin_delete_author(author_id):
    """Eliminar un autor y todos sus libros relacionados"""
    try:
        current_admin_id = get_jwt_identity()
        current_admin = Admin.query.get(current_admin_id)

        if not current_admin:
            return unauthorized('No tiene permiso para eliminar autores')
        
        author = Author.query.get_or_404(author_id)

        # Eliminar en cascada manualmente
        # Primero eliminar todos los libros del autor y sus dependencias
        for libro in author.libros:
            # Eliminar calificaciones/reseñas de este libro
            Rating.query.filter_by(id_libro=libro.id_libros).delete()
            # Eliminar de bibliotecas de usuarios
            UserLibrary.query.filter_by(id_libro=libro.id_libros).delete()
            # Finalmente eliminar el libro
            db.session.delete(libro)
        
        # Ahora eliminar el autor
        db.session.delete(author)
        db.session.commit()

        return jsonify({
            'message': 'Autor y todos sus libros eliminados exitosamente'
        }), 200
    
    except Exception as e:
        db.session.rollback()
        return internal_error(str(e))

# ===== BOOK MANAGEMENT =====
@admin_bp.route('/admin/books/create', methods=['POST'])
@jwt_required()
def admin_create_book():
    try:
        current_admin_id = get_jwt_identity()
        current_admin = Admin.query.get(current_admin_id)

        if not current_admin:
            return unauthorized('No tiene permiso para crear libros')
        
        data = request.get_json()
        
        # Validar campos requeridos
        required_fields = ['titulo_libro', 'id_autor', 'genero_libro']
        for field in required_fields:
            if field not in data or not data[field]:
                return bad_request(f'El campo {field} es requerido')
        
        # ✅ CORREGIR: NO incluir created_at y updated_at
        nuevo_libro = Book(
            titulo_libro=data['titulo_libro'],
            id_autor=data['id_autor'],
            genero_libro=data['genero_libro'],
            descripcion_libros=data.get('descripcion_libros', ''),
            enlace_asin_libro=data.get('enlace_asin_libro', ''),
            enlace_portada_libro=data.get('enlace_portada_libro', '')
            
        )
        
        db.session.add(nuevo_libro)
        db.session.commit()
        
        return jsonify({
            'message': 'Libro creado exitosamente',
            'libro': nuevo_libro.serialize()
        }), 201
        
    except Exception as e:
        db.session.rollback()
        print(f"Error al crear libro: {str(e)}")  # ✅ Debug
        return internal_error(str(e))
        
    except Exception as e:
        db.session.rollback()
        return internal_error(str(e))
    
@admin_bp.route('/admin/books/list', methods=['GET'])
@jwt_required()
def admin_get_all_books():
    """Obtener lista de todos los libros"""
    try:
        current_admin_id = get_jwt_identity()
        current_admin = Admin.query.get(current_admin_id)

        if not current_admin:
            return unauthorized('No tiene permiso para ver libros')
        
        books = Book.query.all()
        return jsonify([book.serialize() for book in books]), 200
    
    except Exception as e:
        return internal_error(str(e))

@admin_bp.route('/admin/books/<int:book_id>/update', methods=['PUT'])
@jwt_required()
def admin_update_book(book_id):
    """Actualizar información de un libro"""
    try:
        current_admin_id = get_jwt_identity()
        current_admin = Admin.query.get(current_admin_id)

        if not current_admin:
            return unauthorized('No tiene permiso para actualizar libros')
        
        book = Book.query.get_or_404(book_id)
        data = request.get_json()

        if 'titulo_libro' in data:
            book.titulo_libro = data['titulo_libro']
        if 'genero_libro' in data:
            book.genero_libro = data['genero_libro']
        if 'descripcion_libros' in data:
            book.descripcion_libros = data['descripcion_libros']
        if 'enlace_portada_libro' in data:
            book.enlace_portada_libro = data['enlace_portada_libro']
        if 'enlace_asin_libro' in data:
            book.enlace_asin_libro = data['enlace_asin_libro']

        db.session.commit()

        return jsonify({
            'message': 'Libro actualizado exitosamente',
            'book': book.serialize()
        }), 200
    
    except Exception as e:
        db.session.rollback()
        return internal_error(str(e))

@admin_bp.route('/admin/books/<int:book_id>/delete', methods=['DELETE'])
@jwt_required()
def admin_delete_book(book_id):
    """Eliminar un libro y todas sus dependencias"""
    try:
        current_admin_id = get_jwt_identity()
        current_admin = Admin.query.get(current_admin_id)

        if not current_admin:
            return unauthorized('No tiene permiso para eliminar libros')
        
        book = Book.query.get_or_404(book_id)

        # Eliminar todas las calificaciones/reseñas del libro
        Rating.query.filter_by(id_libro=book_id).delete()
        
        # Eliminar de todas las bibliotecas de usuarios
        UserLibrary.query.filter_by(id_libro=book_id).delete()
        
        # Finalmente eliminar el libro
        db.session.delete(book)
        db.session.commit()

        return jsonify({
            'message': 'Libro y todas sus dependencias eliminados exitosamente'
        }), 200
    
    except Exception as e:
        db.session.rollback()
        return internal_error(str(e))


# ===== DASHBOARD & STATISTICS =====
@admin_bp.route('/admin/dashboard/overview', methods=['GET'])
@jwt_required()
def admin_dashboard_overview():
    """Obtener estadísticas generales del dashboard"""
    try:
        current_admin_id = get_jwt_identity()
        current_admin = Admin.query.get(current_admin_id)

        if not current_admin:
            return unauthorized('No tiene permiso para ver el dashboard')
        
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

@admin_bp.route('/admin/dashboard/users/stats', methods=['GET'])
@jwt_required()
def admin_users_statistics():
    """Obtener estadísticas de usuarios"""
    try:
        current_admin_id = get_jwt_identity()
        current_admin = Admin.query.get(current_admin_id)

        if not current_admin:
            return unauthorized('No tiene permiso para ver estadísticas')
        
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

@admin_bp.route('/admin/dashboard/authors/stats', methods=['GET'])
@jwt_required()
def admin_authors_statistics():
    """Obtener estadísticas de autores"""
    try:
        current_admin_id = get_jwt_identity()
        current_admin = Admin.query.get(current_admin_id)

        if not current_admin:
            return unauthorized('No tiene permiso para ver estadísticas')
        
        total_authors = Author.query.count()
        authors_with_books = db.session.query(func.count(func.distinct(Book.id_autor))).scalar()
        
        author_most_books = db.session.query(
            Author, func.count(Book.id_libros).label('book_count')
        ).join(Book).group_by(Author.id_autor).order_by(func.count(Book.id_libros).desc()).first()
        
        return jsonify({
            "total_authors": total_authors,
            "authors_with_books": authors_with_books,
            "authors_without_books": total_authors - authors_with_books,
            "top_author": {
                "id_autor": author_most_books[0].id_autor if author_most_books else None,
                "nombre_completo": f"{author_most_books[0].nombre_autor} {author_most_books[0].apellido_autor}" if author_most_books else None,
                "total_libros": author_most_books[1] if author_most_books else 0
            } if author_most_books else None
        }), 200
    
    except Exception as e:
        return internal_error(str(e))

@admin_bp.route('/admin/dashboard/books/stats', methods=['GET'])
@jwt_required()
def admin_books_statistics():
    """Obtener estadísticas de libros"""
    try:
        current_admin_id = get_jwt_identity()
        current_admin = Admin.query.get(current_admin_id)

        if not current_admin:
            return unauthorized('No tiene permiso para ver estadísticas')
        
        total_books = Book.query.count()
        books_with_reviews = db.session.query(func.count(func.distinct(Rating.id_libro))).scalar()
        books_in_libraries = db.session.query(func.count(func.distinct(UserLibrary.id_libro))).scalar()
        average_rating = db.session.query(func.avg(Rating.calificacion)).scalar() or 0
        
        return jsonify({
            "total_books": total_books,
            "books_with_reviews": books_with_reviews,
            "books_in_libraries": books_in_libraries,
            "average_rating": round(float(average_rating), 2),
            "books_without_reviews": total_books - books_with_reviews
        }), 200
    
    except Exception as e:
        return internal_error(str(e))
    # Agregar a admin.py

@admin_bp.route('/admin/authors/<int:author_id>', methods=['GET'])
@jwt_required()
def admin_get_author_detail(author_id):
    """Obtener detalles de un autor específico con sus libros"""
    try:
        current_admin_id = get_jwt_identity()
        current_admin = Admin.query.get(current_admin_id)

        if not current_admin:
            return unauthorized('No tiene permiso para ver autores')
        
        author = Author.query.get_or_404(author_id)
        books = Book.query.filter_by(id_autor=author_id).all()
        
        return jsonify({
            'author': {
                'id_autor': author.id_autor,
                'nombre_autor': author.nombre_autor,
                'apellido_autor': author.apellido_autor,
                'biografia_autor': author.biografia_autor,
                'created_at': author.created_at.isoformat() if author.created_at else None,
                'updated_at': author.updated_at.isoformat() if author.updated_at else None
            },
            'books': [book.serialize() for book in books]
        }), 200
    
    except Exception as e:
        return not_found(str(e))

@admin_bp.route('/admin/books/<int:book_id>', methods=['GET'])
@jwt_required()
def admin_get_book_detail(book_id):
    """Obtener detalles de un libro específico"""
    try:
        current_admin_id = get_jwt_identity()
        current_admin = Admin.query.get(current_admin_id)

        if not current_admin:
            return unauthorized('No tiene permiso para ver libros')
        
        book = Book.query.get_or_404(book_id)
        return jsonify(book.serialize()), 200
    
    except Exception as e:
        return not_found(str(e))