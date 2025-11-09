from flask import Blueprint, request, jsonify
from app.models.user import User
from app import db
from flask_jwt_extended import create_access_token
from werkzeug.security import generate_password_hash, check_password_hash
from app.errors import bad_request, unauthorized, conflict, internal_error

auth_bp = Blueprint('auth', __name__)

@auth_bp.route('/register', methods=['POST'])
def register():
    try:
        data = request.get_json()

        # ✅ Usar los mismos campos que en tu JSON de Postman
        if not data.get('email') or not data.get('password') or not data.get('username'):
            return bad_request('Correo electrónico, nombre de usuario y contraseña son requeridos')
        
        # ✅ Verificar si el email ya existe
        if User.query.filter_by(email_usuario=data['email']).first():
            return conflict('El correo electrónico ya está registrado')
        
        # ✅ Verificar si el nombre de usuario ya existe
        # if User.query.filter_by(nombre_usuario=data['username']).first():
        #     return conflict('El nombre de usuario ya existe')
        
        # ✅ Crear usuario con los campos correctos de tu modelo
        usuario = User(
            nombre_usuario=data['username'],
            apellido_usuario=data.get('last_name', ''),
            email_usuario=data['email'],
            password_usuario=generate_password_hash(data['password']),
            is_active=True
        )

        db.session.add(usuario)
        db.session.commit()

        # ✅ Crear token con id_usuario
        access_token = create_access_token(identity=str(usuario.id_usuario))

        return jsonify({
            'message': 'Usuario registrado exitosamente',
            'access_token': access_token,
            'user': usuario.serialize_public()
        }), 201
    
    except Exception as e:
        db.session.rollback()
        return internal_error(str(e))

@auth_bp.route('/login', methods=['POST'])
def login():
    try:
        data = request.get_json()
        email = data.get('email_usuario')
        password = data.get('password_usuario')
        
        if not email or not password:
            return jsonify({'error': 'Email y contraseña requeridos'}), 400
        
        user = User.query.filter_by(email_usuario=email).first()
        
        if not user:
            return jsonify({'error': 'Credenciales inválidas'}), 401
        
        # ✅ Verificar si el usuario está activo
        if not user.is_active:
            return jsonify({'error': 'Tu cuenta ha sido bloqueada. Por favor, contacta al administrador.'}), 401
        
        # ✅ Verificar contraseña con check_password_hash
        if not check_password_hash(user.password_usuario, password):
            return jsonify({'error': 'Credenciales inválidas'}), 401
        
        # ✅ Crear token
        access_token = create_access_token(identity=str(user.id_usuario))
        
        return jsonify({
            'message': 'Login exitoso',
            'access_token': access_token,
            'user': user.serialize_public()
        }), 200
        
    except Exception as e:
        return jsonify({'error': 'Error interno del servidor'}), 500