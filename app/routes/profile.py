# profile.py (corregido)
from flask import Blueprint, request, jsonify
from app.models.user import User
from app.models import UserLibrary, Rating, Book, Author
from app import db
from app.errors import bad_request, not_found, internal_error, conflict
from flask_jwt_extended import jwt_required, get_jwt_identity

profile_bp = Blueprint('profile', __name__)

@profile_bp.route('/profile', methods=['GET'])
@jwt_required()
def get_user_profile():
    """
    Obtener perfil completo del usuario con estadísticas, biblioteca y reseñas
    """
    try:
        current_user_id = get_jwt_identity()
        
        usuario = User.query.get(current_user_id)
        if not usuario:
            return not_found('Usuario no encontrado')
        
        # Información básica del usuario
        user_basic = {
            'id': usuario.id_usuario,
            'name': f"{usuario.nombre_usuario} {usuario.apellido_usuario}",
            'firstName': usuario.nombre_usuario,
            'lastName': usuario.apellido_usuario,
            'email': usuario.email_usuario,
            'joinDate': usuario.created_at.strftime('%Y-%m-%d') if usuario.created_at else None,
            'lastLogin': usuario.updated_at.strftime('%Y-%m-%d') if usuario.updated_at else None
        }
        
        # Obtener todos los libros en la librería del usuario
        user_library_items = UserLibrary.query.filter_by(id_usuario=current_user_id).all()
        
        # Separar libros por estado de lectura
        books_read = []
        books_reading = []
        books_to_read = []
        
        for item in user_library_items:
            book = Book.query.get(item.id_libro)
            if not book:
                continue
                
            # Obtener la calificación/reseña si existe
            rating = Rating.query.filter_by(
                id_usuario=current_user_id, 
                id_libro=item.id_libro
            ).first()
            
            # Obtener nombre del autor
            author_name = "Autor desconocido"
            if book.id_autor:
                author = Author.query.get(book.id_autor)
                if author:
                    author_name = f"{author.nombre_autor} {author.apellido_autor}"
            
            book_data = {
                'id': book.id_libros,  # ✅ CORREGIDO
                'title': book.titulo_libro,  # ✅ CORREGIDO
                'author': author_name,  # ✅ CORREGIDO
                'cover_url': book.enlace_portada_libro  # ✅ CORREGIDO
            }
            
            # Agregar calificación si existe
            if rating:
                book_data['rating'] = rating.calificacion
            
            # Clasificar por estado de lectura
            if item.estado_lectura == 'leido':
                books_read.append(book_data)
            elif item.estado_lectura == 'leyendo':
                books_reading.append(book_data)
            else:  # 'quiero_leer'
                books_to_read.append(book_data)
        
        # Calcular autores más leídos (solo de libros leídos)
        author_counts = {}
        for book in books_read:
            author = book['author']
            if author != "Autor desconocido":
                author_counts[author] = author_counts.get(author, 0) + 1
        
        top_authors = [
            {'name': author, 'booksCount': count}
            for author, count in sorted(author_counts.items(), key=lambda x: x[1], reverse=True)
        ][:5]  # Top 5 autores
        
        # Obtener reseñas recientes
        recent_reviews = Rating.query.filter_by(id_usuario=current_user_id)\
            .order_by(Rating.created_at.desc())\
            .limit(10)\
            .all()
        
        reviews_data = []
        for review in recent_reviews:
            book = Book.query.get(review.id_libro)
            if book and review.resena:  # Solo incluir si hay reseña escrita
                reviews_data.append({
                    'id': review.id_calificacion,
                    'bookId': book.id_libros,  # ✅ CORREGIDO
                    'bookTitle': book.titulo_libro,  # ✅ CORREGIDO
                    'rating': review.calificacion,
                    'comment': review.resena,
                    'date': review.created_at.strftime('%Y-%m-%d') if review.created_at else None,
                    'likes': 0  # Sistema de likes para futuro
                })
        
        # Respuesta completa
        profile_data = {
            'user': user_basic,
            'statistics': {
                'totalBooksRead': len(books_read),
                'totalBooksReading': len(books_reading),
                'totalBooksToRead': len(books_to_read),
                'totalReviews': len(reviews_data)
            },
            'readingLists': {
                'read': books_read,
                'reading': books_reading,
                'toRead': books_to_read
            },
            'topAuthors': top_authors,
            'recentReviews': reviews_data
        }
        
        return jsonify(profile_data), 200
        
    except Exception as e:
        print(f"Error en get_user_profile: {str(e)}")  # Para debugging
        return internal_error(str(e))


@profile_bp.route('/profile', methods=['PUT'])
@jwt_required()
def update_user_profile():
    """
    Actualizar información básica del perfil del usuario
    """
    try:
        current_user_id = get_jwt_identity()
        data = request.get_json()
        usuario = User.query.get(current_user_id)
        if not usuario:
            return not_found('Usuario no encontrado')
        
        # Actualizar campos permitidos
        if 'username' in data:
            existing_user = User.query.filter(
                User.nombre_usuario == data['username'],
                User.id_usuario != current_user_id
            ).first()
            if existing_user:
                return conflict('El nombre de usuario ya está en uso')
            usuario.nombre_usuario = data['username']
        
        if 'last_name' in data:
            usuario.apellido_usuario = data['last_name']
        
        if 'email' in data:
            existing_email = User.query.filter(
                User.email_usuario == data['email'],
                User.id_usuario != current_user_id
            ).first()
            if existing_email:
                return conflict('El correo electrónico ya está en uso')
            usuario.email_usuario = data['email']
        
        if 'password' in data and data['password']:
            usuario.set_password(data['password'])
        
        db.session.commit()
        
        return jsonify({
            'message': 'Perfil actualizado exitosamente',
            'profile': {
                'user_id': usuario.id_usuario,
                'username': usuario.nombre_usuario,
                'last_name': usuario.apellido_usuario,
                'email': usuario.email_usuario
            }
        }), 200
        
    except Exception as e:
        db.session.rollback()
        return internal_error(str(e))