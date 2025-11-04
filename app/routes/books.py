from flask import Blueprint, request, jsonify
from app.models import Book
from app.models import Author
from app import db
from app.errors import bad_request, not_found, internal_error
from flask_jwt_extended import jwt_required, get_jwt_identity
from sqlalchemy import func

books_bp = Blueprint('books', __name__)

@books_bp.route('/books', methods=['GET'])
def get_books():
    try:
        books = Book.query.all()
        return jsonify([libro.serialize() for libro in books]), 200
    
    except Exception as e:
        return internal_error(str(e))

@books_bp.route('/books/<int:book_id>', methods=['GET'])
def get_book(book_id):
    try:
        libro = Book.query.get_or_404(book_id)
        return jsonify({
            'id': libro.id_libros,
            'title': libro.titulo_libro,
            'author': f"{libro.autor.nombre_autor} {libro.autor.apellido_autor}",
            'genre': libro.genero_libro,
            'description': libro.descripcion_libros,
            'cover_url': libro.enlace_portada_libro,
            'amazon_asin': libro.enlace_asin_libro,
            'publication_date': libro.created_at.strftime('%Y-%m-%d') if libro.created_at else None
        }), 200
    
    except Exception as e:
        return not_found(str(e))

@books_bp.route('/books/genre/<string:genre>', methods=['GET'])
def get_books_by_genre(genre):
    try:
        genre_map = {
            'clasicos': 'Clásicos',
            'ficcion': 'Ficción',
            'no-ficcion': 'No-Ficción',
            'ciencia-ficcion': 'Ciencia Ficción',
            'latinoamericanos': 'Latinoamericano',
            'historia': 'Historia'
        }

        genre_normalized = genre_map.get(genre, genre.title())
        books = Book.query.filter_by(genero_libro=genre_normalized).all()

        return jsonify([{
            'id': libro.id_libros,
            'title': libro.titulo_libro,
            'author': f"{libro.autor.nombre_autor} {libro.autor.apellido_autor}",
            'genre': libro.genero_libro,
            'description': libro.descripcion_libros,
            'cover_url': libro.enlace_portada_libro,
            'amazon_asin': libro.enlace_asin_libro
        } for libro in books]), 200
    
    except Exception as e:
        return internal_error(str(e))

@books_bp.route('/books/search', methods=['GET'])
def search_books():
    try:
        query = request.args.get('q', '')
        if not query:
            return bad_request('Parámetro de búsqueda requerido')
        
        books = Book.query.join(Author).filter(
            db.or_(
                Book.titulo_libro.ilike(f'%{query}%'),
                Author.nombre_autor.ilike(f'%{query}%'),
                Author.apellido_autor.ilike(f'%{query}%')
            )
        ).all()

        return jsonify([{
            'id': libro.id_libros,
            'title': libro.titulo_libro,
            'author': f"{libro.autor.nombre_autor} {libro.autor.apellido_autor}",
            'genre': libro.genero_libro,
            'description': libro.descripcion_libros,
            'cover_url': libro.enlace_portada_libro,
            'amazon_asin': libro.enlace_asin_libro
        } for libro in books]), 200
    
    except Exception as e:
        return internal_error(str(e))

# NUEVAS RUTAS PARA GÉNEROS
@books_bp.route('/books/genres/count', methods=['GET'])
def get_genres_count():
    try:
        # Obtener conteo de libros por género
        genres_count = db.session.query(
            Book.genero_libro, 
            func.count(Book.id_libros).label('count')
        ).group_by(Book.genero_libro).all()
        
        return jsonify([{
            'genre': genre,
            'count': count
        } for genre, count in genres_count]), 200
    
    except Exception as e:
        return internal_error(str(e))

@books_bp.route('/books/genres/stats', methods=['GET'])
def get_genres_stats():
    try:
        # Obtener estadísticas completas por género
        genres_stats = db.session.query(
            Book.genero_libro, 
            func.count(Book.id_libros).label('total_books'),
            func.count(func.distinct(Book.id_autor)).label('unique_authors')
        ).group_by(Book.genero_libro).all()
        
        # Obtener total general
        total_books = db.session.query(func.count(Book.id_libros)).scalar()
        total_genres = db.session.query(func.count(func.distinct(Book.genero_libro))).scalar()
        
        return jsonify({
            'summary': {
                'total_books': total_books,
                'total_genres': total_genres
            },
            'genres': [{
                'genre': genre,
                'total_books': total_books,
                'unique_authors': unique_authors,
                'percentage': round((total_books / total_books) * 100, 2) if total_books > 0 else 0
            } for genre, total_books, unique_authors in genres_stats]
        }), 200
    
    except Exception as e:
        return internal_error(str(e))

@books_bp.route('/books/genres', methods=['GET'])
def get_all_genres():
    try:
        # Obtener lista única de géneros
        genres = db.session.query(Book.genero_libro).distinct().all()
        
        return jsonify({
            'total_genres': len(genres),
            'genres': [genre[0] for genre in genres]
        }), 200
    
    except Exception as e:
        return internal_error(str(e))
    
@books_bp.route('/authors/<int:author_id>/profile', methods=['GET'])
def get_author_profile(author_id):
    """
    Obtener perfil completo del autor para la página de autor en React
    Incluye información del autor y todos sus libros
    """
    try:
        author = Author.query.get_or_404(author_id)
        
        # Obtener todos los libros del autor
        author_books = Book.query.filter_by(id_autor=author_id).all()
        
        # Estadísticas del autor
        total_books = len(author_books)
        genres = list(set([book.genero_libro for book in author_books]))
        
        return jsonify({
            'author': {
                'id_autor': author.id_autor,
                'nombre_completo': f"{author.nombre_autor} {author.apellido_autor}",
                'nombre_autor': author.nombre_autor,
                'apellido_autor': author.apellido_autor,
                'biografia_autor': author.biografia_autor,
                'created_at': author.created_at.isoformat() if author.created_at else None,
            },
            'stats': {
                'total_libros': total_books,
                'generos': genres,
                'total_generos': len(genres)
            },
            'books': [{
                'id_libros': libro.id_libros,
                'titulo_libro': libro.titulo_libro,
                'genero_libro': libro.genero_libro,
                'descripcion_libros': libro.descripcion_libros,
                'enlace_portada_libro': libro.enlace_portada_libro,
                'enlace_asin_libro': libro.enlace_asin_libro,
                'created_at': libro.created_at.isoformat() if libro.created_at else None
            } for libro in author_books]
        }), 200
    
    except Exception as e:
        return not_found(str(e))

@books_bp.route('/authors/search/simple', methods=['GET'])
def search_authors_simple():
    """
    Búsqueda simple de autores para el buscador de React
    Devuelve datos básicos para mostrar en resultados de búsqueda
    """
    try:
        query = request.args.get('q', '')
        if not query or len(query) < 2:
            return jsonify([]), 200  # Devuelve array vacío si query es muy corta
        
        authors = Author.query.filter(
            db.or_(
                Author.nombre_autor.ilike(f'%{query}%'),
                Author.apellido_autor.ilike(f'%{query}%'),
                db.func.concat(Author.nombre_autor, ' ', Author.apellido_autor).ilike(f'%{query}%')
            )
        ).limit(10).all()  # Limitar a 10 resultados para el autocomplete

        return jsonify([{
            'id_autor': autor.id_autor,
            'nombre_completo': f"{autor.nombre_autor} {autor.apellido_autor}",
            'total_libros': len(autor.libros) if autor.libros else 0,
            'primer_genero': autor.libros[0].genero_libro if autor.libros else 'Sin género'
        } for autor in authors]), 200
    
    except Exception as e:
        return internal_error(str(e))


@books_bp.route('/authors', methods=['GET'])
def get_authors():
    try:
        author = Author.query.all()
        return jsonify([autores.serialize() for autores in author]), 200
    
    except Exception as e:
        return internal_error(str(e))
    
