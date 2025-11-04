from flask import Blueprint, request, jsonify
from app.models import User
from app import db
from app.errors import bad_request, not_found, internal_error
from flask_jwt_extended import jwt_required, get_jwt_identity

users_bp = Blueprint('users', __name__)

@users_bp.route('/users/public', methods=['GET'])
def get_public_users():
    """
    Obtener lista pública de usuarios (sin necesidad de token)
    Solo información básica para mostrar en la interfaz
    """
    try:
        users = User.query.filter_by(is_active=True).all()
        
        return jsonify([{
            "id_usuario": user.id_usuario,
            "nombre_usuario": user.nombre_usuario,
            "apellido_usuario": user.apellido_usuario,
            "miembro_desde": user.created_at.strftime('%Y-%m-%d') if user.created_at else None,
            "total_libros_biblioteca": len(user.biblioteca) if user.biblioteca else 0,
            "total_resenas": len(user.calificaciones) if user.calificaciones else 0
        } for user in users]), 200
    
    except Exception as e:
        return internal_error(str(e))
