from flask import Blueprint, request, jsonify
from app.models import Admin, Author, Book
from app import db
from app.errors import bad_request, unauthorized, conflict, internal_error, not_found
from flask_jwt_extended import create_access_token, jwt_required, get_jwt_identity

admin_bp = Blueprint('admin', __name__)

@admin_bp.route('/login', methods=['POST'])
def admin_login():

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
    
@admin_bp.route('/authors', methods=['POST'])
@jwt_required()
def add_author():

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
        
        author = Author(
            nombre_autor=data['nombre_autor'],
            apellido_autor=data['apellido_autor'],
            biografia_autor=data.get('biografia_autor', '')
        )

        db.session.add(author)
        db.session.commit()

        return jsonify({
            'message': 'Autor agregado exitosamente',
            'author': {
                'id_autor': author.id_autor,
                'nombre_completo': f"{author.nombre_autor} {author.apellido_autor}",
                'biografia_autor': author.biografia_autor
            }
        }), 201
    
    except Exception as e:
        db.session.rollback()
        return internal_error(str(e))

@admin_bp.route('/authors/<int:author_id>', methods=['PUT'])
@jwt_required()
def update_author(author_id):

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
        
        db.session.commit()

        return jsonify({
            'message': 'Autor actualizado exitosamente',
            'author': {
                'id_autor': author.id_autor,
                'nombre_completo': f"{author.nombre_autor} {author.apellido_autor}",
                'biografia_autor': author.biografia_autor
            }
        }), 200
    
    except Exception as e:
        db.session.rollback()
        return internal_error(str(e))
    
@admin_bp.route('/authors/<int:author_id>', methods=['DELETE'])
@jwt_required()
def delete_author(author_id):

    try:
        current_admin_id = get_jwt_identity()
        current_admin = Admin.query.get(current_admin_id)

        if not current_admin:
            return unauthorized('No tiene permiso para eliminar autores')
        
        author = Author.query.get_or_404(author_id)

        if author.libros:
            return conflict('No se puede eliminar un autor que tiene libros asociados')
        
        db.session.delete(author)
        db.session.commit()

        return jsonify({
            'message': 'Autor eliminado exitosamente'
        }), 200
    
    except Exception as e:
        db.session.rollback()
        return internal_error(str(e))
    
@admin_bp.route('/books', methods=['POST'])
@jwt_required()
def add_book():

    try:
        current_admin_id = get_jwt_identity()
        current_admin = Admin.query.get(current_admin_id)

        if not current_admin:
            return unauthorized('No tiene permiso para agregar libros')
        
        data = request.get_json()

        required_fields = ['titulo_libro', 'id_autor', 'genero_libro']
        for field in required_fields:
            if not data.get(field):
                return bad_request(f'El campo {field} es requerido')
            
        author = Author.query.get(data['id_autor'])
        if not author:
            return not_found('Autor no encontrado')
        
        book = Book(
            titulo_libro=data['titulo_libro'],
            id_autor=data['id_autor'],
            genero_libro=data['genero_libro'],
            descripcion_libros=data.get('descripcion_libros', ''),
            enlace_portada_libro=data.get('enlace_portada_libro', ''),
            enlace_asin_libro=data.get('enlace_asin_libro', '')
        )

        db.session.add(book)
        db.session.commit()

        return jsonify({
            'message': 'Libro agregado exitosamente',
            'book': book.serialize()
        }), 201
    
    except Exception as e:
        db.session.rollback()
        return internal_error(str(e))
    
@admin_bp.route('/books/<int:book_id>', methods=['PUT'])
@jwt_required()
def update_book(book_id):

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
    
@admin_bp.route('/books/<int:book_id>', methods=['DELETE'])
@jwt_required()
def delete_book(book_id):

    try:
        current_admin_id = get_jwt_identity()
        current_admin = Admin.query.get(current_admin_id)

        if not current_admin:
            return unauthorized('No tiene permiso para eliminar libros')
        
        book = Book.query.get_or_404(book_id)

        db.session.delete(book)
        db.session.commit()

        return jsonify({
            'message': 'Libro eliminado exitosamente'
        }), 200
    
    except Exception as e:
        db.session.rollback()
        return internal_error(str(e))
    
@admin_bp.route('/profile', methods=['GET'])
@jwt_required()
def get_admin_profile():

    try:
        current_admin_id = get_jwt_identity()
        admin = Admin.query.get(current_admin_id)

        if not admin:
            return not_found('Administrador no encontrado')
        
        return jsonify(admin.serialize()), 200
    
    except Exception as e:
        return internal_error(str(e))
    
@admin_bp.route('/profile', methods=['PUT'])
@jwt_required()
def update_admin_profile():

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