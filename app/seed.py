import os
import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app import create_app
from app.database import db
from app.models.user import User
from app.models.author import Author
from app.models.book import Book
from app.models.rating import Rating
from app.models.user_library import UserLibrary
import random
from werkzeug.security import generate_password_hash
from app.models.admin import Admin




app = create_app()

def seed_database():
    with app.app_context():
        print("🗑️ Limpiando base de datos...")
        
        # Limpiar tablas en el orden correcto (respetando foreign keys)
        UserLibrary.query.delete()
        Rating.query.delete()
        Book.query.delete()
        Author.query.delete()
        User.query.delete()
        Admin.query.delete()
        
        # ===== CREAR ADMIN PRINCIPAL =====
        print("👨‍💼 Creando administrador principal...")
        admin = Admin(
            nombre_admin="Administrador Principal",
            email_admin="admin@booketlist.com",
            password_admin="admin123"  # Se hashea automáticamente en el modelo
        )
        db.session.add(admin)
        db.session.commit()
        print(f"✓ Admin creado - Email: {admin.email_admin}")
        
        print("👥 Creando autores reales...")
        autores_data = [
            # Clásicos
            {"nombre": "Miguel de", "apellido": "Cervantes", "biografia": "Escritor español, autor de Don Quijote de la Mancha, considerada la primera novela moderna."},
            {"nombre": "Jane", "apellido": "Austen", "biografia": "Novelista británica conocida por sus novelas de crítica social y romance."},
            {"nombre": "Fiódor", "apellido": "Dostoyevski", "biografia": "Escritor ruso, uno de los principales novelistas de la literatura universal."},
            {"nombre": "Herman", "apellido": "Melville", "biografia": "Escritor estadounidense, autor de Moby Dick y otras obras maestras."},
            {"nombre": "Homero", "apellido": "", "biografia": "Poeta griego antiguo, autor de La Ilíada y La Odisea."},
            {"nombre": "Marcel", "apellido": "Proust", "biografia": "Novelista francés, autor de En busca del tiempo perdido."},
            {"nombre": "William", "apellido": "Shakespeare", "biografia": "Dramaturgo y poeta inglés, considerado el escritor más importante en lengua inglesa."},
            {"nombre": "Dante", "apellido": "Alighieri", "biografia": "Poeta italiano, autor de La Divina Comedia."},
            {"nombre": "León", "apellido": "Tolstói", "biografia": "Novelista ruso, autor de Guerra y Paz y Anna Karénina."},
            {"nombre": "Charles", "apellido": "Dickens", "biografia": "Escritor británico, creador de algunos de los personajes más memorables de la literatura."},
            
            # No-Ficción
            {"nombre": "Yuval Noah", "apellido": "Harari", "biografia": "Historiador y escritor israelí, autor de Sapiens y Homo Deus."},
            {"nombre": "Tara", "apellido": "Westover", "biografia": "Escritora estadounidense, conocida por su memoir Una educación."},
            {"nombre": "Eckhart", "apellido": "Tolle", "biografia": "Escritor espiritual alemán, autor de El poder del ahora."},
            {"nombre": "Daniel", "apellido": "Kahneman", "biografia": "Psicólogo israelí-estadounidense, premio Nobel de Economía."},
            {"nombre": "Stephen", "apellido": "Hawking", "biografia": "Físico teórico y cosmólogo británico, autor de Historia del tiempo."},
            {"nombre": "Ana", "apellido": "Frank", "biografia": "Escritora alemana, autora del diario que lleva su nombre."},
            {"nombre": "Jared", "apellido": "Diamond", "biografia": "Geógrafo e historiador estadounidense, autor de Armas, gérmenes y acero."},
            {"nombre": "Viktor", "apellido": "Frankl", "biografia": "Neurólogo y psiquiatra austríaco, fundador de la logoterapia."},
            {"nombre": "Stephen R.", "apellido": "Covey", "biografia": "Escritor y conferenciante estadounidense, autor de Los 7 hábitos de la gente altamente efectiva."},
            
            # Ciencia Ficción
            {"nombre": "Frank", "apellido": "Herbert", "biografia": "Escritor estadounidense de ciencia ficción, autor de Dune."},
            {"nombre": "Isaac", "apellido": "Asimov", "biografia": "Escritor y bioquímico ruso, autor de la serie Fundación."},
            {"nombre": "George", "apellido": "Orwell", "biografia": "Escritor y periodista británico, autor de 1984 y Rebelión en la granja."},
            {"nombre": "Aldous", "apellido": "Huxley", "biografia": "Escritor británico, autor de Un mundo feliz."},
            {"nombre": "William", "apellido": "Gibson", "biografia": "Escritor canadiense-estadounidense, pionero del cyberpunk."},
            {"nombre": "Orson Scott", "apellido": "Card", "biografia": "Escritor estadounidense de ciencia ficción, autor de El juego de Ender."},
            {"nombre": "Ray", "apellido": "Bradbury", "biografia": "Escritor estadounidense de ciencia ficción, autor de Fahrenheit 451."},
            {"nombre": "Ursula K.", "apellido": "Le Guin", "biografia": "Escritora estadounidense de ciencia ficción y fantasía."},
            {"nombre": "Stanisław", "apellido": "Lem", "biografia": "Escritor polaco de ciencia ficción, filósofo y ensayista."},
            
            # Ficción General
            {"nombre": "F. Scott", "apellido": "Fitzgerald", "biografia": "Escritor estadounidense, autor de El gran Gatsby."},
            {"nombre": "Harper", "apellido": "Lee", "biografia": "Escritora estadounidense, autora de Matar a un ruiseñor."},
            {"nombre": "J.D.", "apellido": "Salinger", "biografia": "Escritor estadounidense, autor de El guardián entre el centeno."},
            {"nombre": "J.R.R.", "apellido": "Tolkien", "biografia": "Escritor británico, autor de El Señor de los Anillos."},
            {"nombre": "Dan", "apellido": "Brown", "biografia": "Escritor estadounidense, autor de El código Da Vinci."},
            {"nombre": "Suzanne", "apellido": "Collins", "biografia": "Escritora estadounidense, autora de Los juegos del hambre."},
            {"nombre": "Carlos Ruiz", "apellido": "Zafón", "biografia": "Escritor español, autor de La sombra del viento."},
            {"nombre": "J.K.", "apellido": "Rowling", "biografia": "Escritora británica, autora de la serie Harry Potter."},
            
            # Latinoamericanos
            {"nombre": "Gabriel García", "apellido": "Márquez", "biografia": "Escritor colombiano, premio Nobel de Literatura 1982."},
            {"nombre": "Isabel", "apellido": "Allende", "biografia": "Escritora chilena, una de las novelistas más leídas del mundo."},
            {"nombre": "Julio", "apellido": "Cortázar", "biografia": "Escritor argentino, autor de Rayuela."},
            {"nombre": "Juan", "apellido": "Rulfo", "biografia": "Escritor mexicano, autor de Pedro Páramo."},
            {"nombre": "Mario", "apellido": "Vargas Llosa", "biografia": "Escritor peruano, premio Nobel de Literatura 2010."},
            {"nombre": "Ernesto", "apellido": "Sabato", "biografia": "Escritor argentino, autor de El túnel."},
            {"nombre": "Laura", "apellido": "Esquivel", "biografia": "Escritora mexicana, autora de Como agua para chocolate."},
            {"nombre": "Jorge Luis", "apellido": "Borges", "biografia": "Escritor argentino, uno de los autores más importantes del siglo XX."},
            {"nombre": "Roberto", "apellido": "Bolaño", "biografia": "Escritor chileno, autor de Los detectives salvajes."},
            
            # Historia
            {"nombre": "Ken", "apellido": "Follett", "biografia": "Escritor británico, autor de novelas históricas bestsellers."},
            {"nombre": "Umberto", "apellido": "Eco", "biografia": "Escritor italiano, autor de El nombre de la rosa."},
            {"nombre": "Chimamanda Ngozi", "apellido": "Adichie", "biografia": "Escritora nigeriana, autora de Americanah."},
            {"nombre": "Stefan", "apellido": "Zweig", "biografia": "Escritor austríaco, autor de El mundo de ayer."},
            {"nombre": "Victor", "apellido": "Hugo", "biografia": "Escritor francés, autor de Los miserables."}
        ]
        
        autores = []
        for autor_data in autores_data:
            autor = Author(
                nombre_autor=autor_data["nombre"],
                apellido_autor=autor_data["apellido"],
                biografia_autor=autor_data["biografia"]
            )
            db.session.add(autor)
            autores.append(autor)
        
        db.session.commit()
        print(f"✓ {len(autores)} autores creados")
        
        print("📚 Creando libros reales...")
        libros_data = [
            # CLÁSICOS
            {
                "titulo": "Don Quijote de la Mancha",
                "autor_index": 0,
                "genero": "Clásicos",
                "descripcion": "Las aventuras del ingenioso hidalgo que pierde la razón por leer novelas de caballería y sale a desfacer entuertos.",
                "asin": "8491057536",
                "portada": "https://m.media-amazon.com/images/I/81-ylKA1wJL._SL1500_.jpg"
            },
            {
                "titulo": "Orgullo y Prejuicio", 
                "autor_index": 1,
                "genero": "Clásicos",
                "descripcion": "Elizabeth Bennet y Mr. Darcy superan sus prejuicios iniciales en esta brillante sátira sobre el matrimonio y la sociedad inglesa.",
                "asin": "8491051325",
                "portada": "https://m.media-amazon.com/images/I/71KZzetNT9L._SL1500_.jpg"
            },
            {
                "titulo": "Crimen y Castigo",
                "autor_index": 2,
                "genero": "Clásicos", 
                "descripcion": "Raskólnikov asesina a una anciana usurera y enfrenta las consecuencias psicológicas de su acto en la San Petersburgo del siglo XIX.",
                "asin": "B0DWKBCSL2",
                "portada": "https://m.media-amazon.com/images/I/71jl4XMVEKL._SL1329_.jpg"
            },
            {
                "titulo": "Moby Dick",
                "autor_index": 3,
                "genero": "Clásicos",
                "descripcion": "El capitán Ahab persigue obsesivamente a la ballena blanca que le arrancó una pierna en una travesía hacia la autodestrucción.",
                "asin": "8491050205", 
                "portada": "https://m.media-amazon.com/images/I/81-jgO4Zm8L._SL1500_.jpg"
            },
            {
                "titulo": "La Odisea",
                "autor_index": 4,
                "genero": "Clásicos",
                "descripcion": "El épico viaje de Odiseo de regreso a Ítaca tras la Guerra de Troya, enfrentando monstruos, dioses y su propio destino.",
                "asin": "8413625173",
                "portada": "https://m.media-amazon.com/images/I/61O4h3WIM0L._SL1050_.jpg"
            },
            {
                "titulo": "Los Hermanos Karamazov",
                "autor_index": 2,
                "genero": "Clásicos",
                "descripcion": "Tres hermanos de personalidades opuestas enfrentan cuestiones de fe, moralidad y libre albedrío tras la muerte de su padre.",
                "asin": "8491050051",
                "portada": "https://m.media-amazon.com/images/I/81yq7rUwYmL._SL1500_.jpg"
            },
            {
                "titulo": "En Busca del Tiempo Perdido",
                "autor_index": 5,
                "genero": "Clásicos",
                "descripcion": "Monumental exploración de la memoria, el tiempo y la sociedad francesa a través de las reminiscencias del narrador.",
                "asin": "B09FS9PMKS",
                "portada": "https://m.media-amazon.com/images/I/61CNCVKq6cL._SL1500_.jpg"
            },
            {
                "titulo": "Hamlet",
                "autor_index": 6,
                "genero": "Clásicos",
                "descripcion": "El príncipe de Dinamarca busca vengar el asesinato de su padre mientras lucha contra la duda, la locura y el destino.",
                "asin": "B0CT1FB5QN",
                "portada": "https://m.media-amazon.com/images/I/71uz9igbHrL._SL1500_.jpg"
            },
            {
                "titulo": "La Divina Comedia",
                "autor_index": 7,
                "genero": "Clásicos",
                "descripcion": "Dante viaja por el Infierno, el Purgatorio y el Paraíso en una obra maestra alegórica sobre el alma y la salvación.",
                "asin": "1518711375",
                "portada": "https://m.media-amazon.com/images/I/71WJbXGxPdL._SL1360_.jpg"
            },
            {
                "titulo": "Guerra y Paz", 
                "autor_index": 8,
                "genero": "Clásicos",
                "descripcion": "Familias aristocráticas rusas viven amores, tragedias y transformaciones durante las guerras napoleónicas en esta épica monumental.",
                "asin": "B091FMWH1Z",
                "portada": "https://m.media-amazon.com/images/I/91bx-1HHXGL._SL1500_.jpg"
            },

            # NO-FICCIÓN
            {
                "titulo": "Sapiens: De Animales a Dioses",
                "autor_index": 10,
                "genero": "No-Ficción", 
                "descripcion": "Una exploración fascinante de la historia de la humanidad desde nuestros orígenes hasta la actualidad y nuestro futuro.",
                "asin": "841939971X",
                "portada": "https://m.media-amazon.com/images/I/717sO7vkyUL._SL1500_.jpg"
            },
            {
                "titulo": "Una Educación",
                "autor_index": 11,
                "genero": "No-Ficción",
                "descripcion": "Memorias de una mujer criada por fundamentalistas mormones que nunca fue a la escuela hasta obtener un doctorado en Cambridge.",
                "asin": "B0D1RBR9XW", 
                "portada": "https://m.media-amazon.com/images/I/71JoUjDA0CL._SL1500_.jpg"
            },
            {
                "titulo": "El Poder del Ahora",
                "autor_index": 12,
                "genero": "No-Ficción",
                "descripcion": "Guía espiritual para vivir en el momento presente, liberándose del dolor emocional del pasado y la ansiedad del futuro.",
                "asin": "8484450341",
                "portada": "https://m.media-amazon.com/images/I/31gCZ3hEQ5L.jpg"
            },
            {
                "titulo": "Pensar Rápido, Pensar Despacio",
                "autor_index": 13,
                "genero": "No-Ficción",
                "descripcion": "El premio Nobel de Economía explica los dos sistemas de pensamiento que moldean nuestras decisiones y juicios cotidianos.",
                "asin": "B085NZ4HVD",
                "portada": "https://m.media-amazon.com/images/I/71sy-wpVL-L._SL1500_.jpg"
            },
            {
                "titulo": "Historia del tiempo: Del big bang a los agujeros negros",
                "autor_index": 14,
                "genero": "No-Ficción",
                "descripcion": "El célebre físico explica los grandes misterios del universo: agujeros negros, el Big Bang y la naturaleza del tiempo.",
                "asin": "8420651990",
                "portada": "https://m.media-amazon.com/images/I/71PxtZIcvML._SL1500_.jpg"
            },
            {
                "titulo": "El Diario de Ana Frank", 
                "autor_index": 15,
                "genero": "No-Ficción",
                "descripcion": "El testimonio auténtico de una adolescente judía escondida durante el Holocausto, símbolo universal de esperanza y resistencia.",
                "asin": "0525565884",
                "portada": "https://m.media-amazon.com/images/I/71QANHhE33L._SL1500_.jpg"
            },
            {
                "titulo": "Homo Deus: Breve Historia del Mañana",
                "autor_index": 10,
                "genero": "No-Ficción",
                "descripcion": "Explora el futuro de la humanidad en una era donde la tecnología podría convertirnos en dioses o hacernos obsoletos.",
                "asin": "8499926711",
                "portada": "https://m.media-amazon.com/images/I/81kZpuvRoFL._SL1500_.jpg"
            },
            {
                "titulo": "Armas, Gérmenes y Acero",
                "autor_index": 16,
                "genero": "No-Ficción",
                "descripcion": "Análisis profundo sobre cómo factores geográficos y ambientales determinaron el destino de las civilizaciones humanas.",
                "asin": "8499928714",
                "portada": "https://m.media-amazon.com/images/I/81etu+U84iL._SL1500_.jpg"
            },
            {
                "titulo": "El Hombre en Busca de Sentido",
                "autor_index": 17,
                "genero": "No-Ficción", 
                "descripcion": "El psiquiatra sobreviviente del Holocausto explora cómo encontrar propósito y significado incluso en el sufrimiento extremo.",
                "asin": "8425451094",
                "portada": "https://m.media-amazon.com/images/I/61yfWdq5+zL._SL1050_.jpg"
            },
            {
                "titulo": "Los Siete Hábitos de la Gente Altamente Efectiva",
                "autor_index": 18,
                "genero": "No-Ficción",
                "descripcion": "Principios fundamentales para el desarrollo personal y profesional que han transformado millones de vidas en todo el mundo.",
                "asin": "6075695591",
                "portada": "https://m.media-amazon.com/images/I/617AqnsUdqL._SL1500_.jpg"
            },

            # CIENCIA FICCIÓN
            {
                "titulo": "Dune",
                "autor_index": 19,
                "genero": "Ciencia Ficción",
                "descripcion": "Paul Atreides debe sobrevivir en el desierto planeta Arrakis, fuente de la sustancia más valiosa del universo: la especia.",
                "asin": "8466363408",
                "portada": "https://m.media-amazon.com/images/I/91bNnC0hTFL._SL1500_.jpg"
            },
            {
                "titulo": "Fundación",
                "autor_index": 20,
                "genero": "Ciencia Ficción",
                "descripcion": "Hari Seldon predice la caída del Imperio Galáctico y crea la Fundación para preservar el conocimiento y acortar la edad oscura.",
                "asin": "8497599241",
                "portada": "https://m.media-amazon.com/images/I/91ktHAuXOCL._SL1500_.jpg"
            },
            {
                "titulo": "1984",
                "autor_index": 21,
                "genero": "Ciencia Ficción",
                "descripcion": "Una distopía totalitaria donde el Gran Hermano controla cada aspecto de la vida mediante vigilancia, propaganda y manipulación.",
                "asin": "6073844328",
                "portada": "https://m.media-amazon.com/images/I/51GPJUr5v0L._SL1157_.jpg"
            },
            {
                "titulo": "Un Mundo Feliz",
                "autor_index": 22,
                "genero": "Ciencia Ficción",
                "descripcion": "En una sociedad futurista donde todos son felices mediante condicionamiento y drogas, un hombre cuestiona este orden perfecto.",
                "asin": "8466350942",
                "portada": "https://m.media-amazon.com/images/I/81glRrzOepL._SL1500_.jpg"
            },
            {
                "titulo": "Neuromante",
                "autor_index": 23,
                "genero": "Ciencia Ficción",
                "descripcion": "Case, un hacker caído en desgracia, es contratado para el último trabajo: hackear una inteligencia artificial en el ciberespacio.",
                "asin": "8445070843",
                "portada": "https://m.media-amazon.com/images/I/81ZE-kY+ynL._SL1500_.jpg"
            },
            {
                "titulo": "El Juego de Ender",
                "autor_index": 24,
                "genero": "Ciencia Ficción",
                "descripcion": "Ender Wiggin, un niño genio, es entrenado en una escuela militar espacial para liderar la lucha contra una invasión alienígena.",
                "asin": "8420434191",
                "portada": "https://m.media-amazon.com/images/I/91fqbLUmU0L._SL1500_.jpg"
            },
            {
                "titulo": "Fahrenheit 451",
                "autor_index": 25,
                "genero": "Ciencia Ficción",
                "descripcion": "En una sociedad donde los libros están prohibidos, el bombero Guy Montag comienza a cuestionar su trabajo de quemar literatura.",
                "asin": "1644730537",
                "portada": "https://m.media-amazon.com/images/I/713hU5z9iaL._SL1500_.jpg"
            },
            {
                "titulo": "La Mano Izquierda de la Oscuridad",
                "autor_index": 26,
                "genero": "Ciencia Ficción",
                "descripcion": "Un enviado humano debe navegar la política de un planeta helado habitado por seres andróginos en busca de una alianza.",
                "asin": "6070799895",
                "portada": "https://m.media-amazon.com/images/I/813AqVVbDLL._SL1500_.jpg"
            },
            {
                "titulo": "Yo, Robot",
                "autor_index": 20,
                "genero": "Ciencia Ficción",
                "descripcion": "Historias interconectadas exploran las Tres Leyes de la Robótica y las complejas relaciones entre humanos y máquinas inteligentes.",
                "asin": "8435021343",
                "portada": "https://m.media-amazon.com/images/I/71x-U3x5N2L._SL1500_.jpg"
            },
            {
                "titulo": "Solaris",
                "autor_index": 27,
                "genero": "Ciencia Ficción",
                "descripcion": "Científicos en una estación espacial estudian un océano viviente que materializa sus memorias más dolorosas y profundas.",
                "asin": "8445076825",
                "portada": "https://m.media-amazon.com/images/I/61DC0GVd5LL._SL1181_.jpg"
            },

            # FICCIÓN GENERAL
            {
                "titulo": "El Gran Gatsby",
                "autor_index": 28,
                "genero": "Ficción",
                "descripcion": "Jay Gatsby persigue su sueño americano y un amor perdido en el glamuroso y corrupto mundo de Nueva York en los años veinte.",
                "asin": "8466350969",
                "portada": "https://m.media-amazon.com/images/I/912jMzwrRQL._SL1500_.jpg"
            },
            {
                "titulo": "Matar a un Ruiseñor",
                "autor_index": 29,
                "genero": "Ficción",
                "descripcion": "Scout Finch narra la defensa de su padre de un hombre negro acusado injustamente en el sur de Estados Unidos durante la Depresión.",
                "asin": "0718076370",
                "portada": "https://m.media-amazon.com/images/I/81+j6JIEweL._SL1500_.jpg"
            },
            {
                "titulo": "El Guardián entre el Centeno",
                "autor_index": 30,
                "genero": "Ficción",
                "descripcion": "Holden Caulfield vaga por Nueva York tras ser expulsado de su escuela, criticando la hipocresía del mundo adulto.",
                "asin": "8420674206",
                "portada": "https://m.media-amazon.com/images/I/61fwcnFmmpL._SL1080_.jpg"
            },
            {
                "titulo": "El Señor de los Anillos: La Comunidad del Anillo",
                "autor_index": 31,
                "genero": "Ficción",
                "descripcion": "Frodo Bolsón inicia una peligrosa misión para destruir un anillo mágico que amenaza con sumir la Tierra Media en la oscuridad.",
                "asin": "6070792238",
                "portada": "https://m.media-amazon.com/images/I/81LYyyLeR5L._SL1500_.jpg"
            },
            {
                "titulo": "El Código Da Vinci",
                "autor_index": 32,
                "genero": "Ficción",
                "descripcion": "Robert Langdon descifra símbolos antiguos en una carrera contrarreloj para resolver un misterio que sacudiría los cimientos del cristianismo.",
                "asin": "8408163159",
                "portada": "https://m.media-amazon.com/images/I/71cmxCYAntL._SL1003_.jpg"
            },
            {
                "titulo": "Los Juegos del Hambre",
                "autor_index": 33,
                "genero": "Ficción",
                "descripcion": "Katniss Everdeen se ofrece como tributo para competir en un brutal reality show donde solo uno de 24 jóvenes sobrevivirá.",
                "asin": "6073807848",
                "portada": "https://m.media-amazon.com/images/I/71N9ipxBq-L._SL1500_.jpg"
            },
            {
                "titulo": "La Sombra del Viento",
                "autor_index": 34,
                "genero": "Ficción",
                "descripcion": "En la Barcelona de posguerra, Daniel descubre un libro misterioso que lo lleva a desentrañar secretos oscuros del pasado.",
                "asin": "8408299751",
                "portada": "https://m.media-amazon.com/images/I/61nVH-yc7-L._SL1050_.jpg"
            },
            {
                "titulo": "Harry Potter y la Piedra Filosofal",
                "autor_index": 35,
                "genero": "Ficción",
                "descripcion": "Harry Potter descubre que es un mago y comienza su educación en Hogwarts, donde enfrenta misterios y magia oscura.",
                "asin": "8478884459",
                "portada": "https://m.media-amazon.com/images/I/61mEUsasD-L._SL1036_.jpg"
            },

            # LATINOAMERICANOS
            {
                "titulo": "Cien Años de Soledad",
                "autor_index": 36,
                "genero": "Latinoamericano",
                "descripcion": "La saga de la familia Buendía en el pueblo mítico de Macondo, obra cumbre del realismo mágico latinoamericano.",
                "asin": "0307474720",
                "portada": "https://m.media-amazon.com/images/I/81n2i30X+5L._SL1500_.jpg"
            },
            {
                "titulo": "La Casa de los Espíritus",
                "autor_index": 37,
                "genero": "Latinoamericano",
                "descripcion": "Tres generaciones de mujeres de la familia Trueba navegan amor, política y poderes sobrenaturales en Chile.",
                "asin": "0525433473",
                "portada": "https://m.media-amazon.com/images/I/81sf9LHQcML._SL1500_.jpg"
            },
            {
                "titulo": "Rayuela",
                "autor_index": 38,
                "genero": "Latinoamericano",
                "descripcion": "Una novela experimental que puede leerse en múltiples órdenes, explorando el amor y la búsqueda existencial.",
                "asin": "8437624746",
                "portada": "https://m.media-amazon.com/images/I/51lnhKqPnQL._SL1050_.jpg"
            },
            {
                "titulo": "Pedro Páramo",
                "autor_index": 39,
                "genero": "Latinoamericano",
                "descripcion": "Juan Preciado busca a su padre en Comala, un pueblo habitado por fantasmas y voces del pasado mexicano.",
                "asin": "080216093X",
                "portada": "https://m.media-amazon.com/images/I/81IfreXInWL._SL1500_.jpg"
            },
            {
                "titulo": "La Ciudad y los Perros",
                "autor_index": 40,
                "genero": "Latinoamericano",
                "descripcion": "Cadetes de un colegio militar en Lima enfrentan violencia, código de honor y corrupción en la sociedad peruana.",
                "asin": "8420454052",
                "portada": "https://m.media-amazon.com/images/I/81u8RSD9R7L._SL1500_.jpg"
            },
            {
                "titulo": "El Túnel",
                "autor_index": 41,
                "genero": "Latinoamericano",
                "descripcion": "Un pintor obsesionado narra desde prisión el asesinato de la única mujer que comprendió su arte en Buenos Aires.",
                "asin": "6070784057",
                "portada": "https://m.media-amazon.com/images/I/715wzJ+wgxL._SL1500_.jpg"
            },
            {
                "titulo": "Como Agua para Chocolate",
                "autor_index": 42,
                "genero": "Latinoamericano",
                "descripcion": "Tita expresa emociones prohibidas a través de la cocina, mezclando recetas con realismo mágico en la Revolución Mexicana.",
                "asin": "0385721234",
                "portada": "https://m.media-amazon.com/images/I/71ANghTe2rL._SL1200_.jpg"
            },
            {
                "titulo": "El Aleph",
                "autor_index": 43,
                "genero": "Latinoamericano",
                "descripcion": "Colección de cuentos metafísicos donde Borges explora infinitos, laberintos y los límites de la realidad y el tiempo.",
                "asin": "846634683X",
                "portada": "https://m.media-amazon.com/images/I/81jFjE9rt6L._SL1500_.jpg"
            },
            {
                "titulo": "La Fiesta del Chivo",
                "autor_index": 40,
                "genero": "Latinoamericano",
                "descripcion": "La dictadura de Trujillo en República Dominicana vista a través del retorno de una mujer y el asesinato del tirano.",
                "asin": "8420434647",
                "portada": "https://m.media-amazon.com/images/I/71lRLtiOAGL._SL1050_.jpg"
            },
            {
                "titulo": "Los Detectives Salvajes",
                "autor_index": 44,
                "genero": "Latinoamericano",
                "descripcion": "Jóvenes poetas buscan a una escritora desaparecida en México, explorando la bohemia literaria de los años setenta.",
                "asin": "8420423939",
                "portada": "https://m.media-amazon.com/images/I/612e-xhmW9L._SL1050_.jpg"
            },

            # HISTORIA
            {
                "titulo": "Una Historia de Dos Ciudades",
                "autor_index": 9,
                "genero": "Historia",
                "descripcion": "Durante la Revolución Francesa, las vidas de familias en Londres y París se entrelazan en una historia de sacrificio y redención.",
                "asin": "8418211563",
                "portada": "https://m.media-amazon.com/images/I/91oMKu1JF6S._SL1500_.jpg"
            },
            {
                "titulo": "Los Pilares de la Tierra",
                "autor_index": 45,
                "genero": "Historia",
                "descripcion": "La construcción de una catedral gótica en la Inglaterra medieval sirve de telón para intrigas, ambiciones y luchas de poder.",
                "asin": "8401328519",
                "portada": "https://m.media-amazon.com/images/I/51SwGPdq3HL.jpg"
            },
            {
                "titulo": "El Nombre de la Rosa",
                "autor_index": 46,
                "genero": "Historia",
                "descripcion": "Un fraile franciscano investiga misteriosos asesinatos en una abadía italiana del siglo XIV llena de secretos y herejías.",
                "asin": "8426403565",
                "portada": "https://m.media-amazon.com/images/I/816Z+coEZ8L._SL1500_.jpg"
            },
            {
                "titulo": "Todos Deberíamos Ser Feministas",
                "autor_index": 47,
                "genero": "Historia",
                "descripcion": "Un ensayo personal que examina la historia y el significado del feminismo en el contexto africano y global contemporáneo.",
                "asin": "8439730489",
                "portada": "https://m.media-amazon.com/images/I/71mEPWrODwL._SL1500_.jpg"
            },
            {
                "titulo": "El Mundo de Ayer",
                "autor_index": 48,
                "genero": "Historia",
                "descripcion": "Memorias del escritor austriaco sobre la Europa culta anterior a las guerras mundiales y su destrucción por el totalitarismo.",
                "asin": "B09S68C8WZ",
                "portada": "https://m.media-amazon.com/images/I/61f6TsIQuvL._SL1491_.jpg"
            },
            {
                "titulo": "Los Miserables",
                "autor_index": 49,
                "genero": "Historia",
                "descripcion": "Jean Valjean busca redención en la Francia del siglo XIX, en una épica historia sobre justicia, amor y revolución social.",
                "asin": "B0CFZFJYKS",
                "portada": "https://m.media-amazon.com/images/I/71aLbjCBRnL._SL1500_.jpg"
            }
        ]

        libros = []
        for libro_data in libros_data:
            libro = Book(
                titulo_libro=libro_data["titulo"],
                id_autor=autores[libro_data["autor_index"]].id_autor,
                genero_libro=libro_data["genero"],
                descripcion_libros=libro_data["descripcion"],
                enlace_asin_libro=libro_data["asin"],
                enlace_portada_libro=libro_data["portada"]
            )
            db.session.add(libro)
            libros.append(libro)
        
        db.session.commit()
        print(f"✓ {len(libros)} libros reales creados")
        
        print("👤 Creando usuarios de prueba...")
        usuarios = []
        nombres_usuarios = ["Ana", "Carlos", "María", "José", "Laura"]
        apellidos_usuarios = ["García", "Rodríguez", "Martínez", "López", "Pérez"]
        
        for i in range(5):
            usuario = User(
                nombre_usuario=nombres_usuarios[i],
                apellido_usuario=apellidos_usuarios[i],
                email_usuario=f"usuario{i+1}@biblioteca.com",
                password_usuario=generate_password_hash('password123'),
                is_active=True
            )
            db.session.add(usuario)
            usuarios.append(usuario)
        
        db.session.commit()
        print(f"✓ {len(usuarios)} usuarios creados")
        
        print("⭐ Creando calificaciones realistas...")
        reseñas_ejemplo = [
            "Excelente libro, muy recomendado.",
            "Una obra maestra de la literatura.",
            "Interesante pero un poco largo.",
            "Me encantó, lo leería de nuevo.",
            "Buen desarrollo de personajes.",
            "Lectura obligatoria para todos.",
            "No es mi género favorito pero está bien.",
            "Muy bien escrito y emocionante.",
            "Clásico que todos deberían leer.",
            "Me sorprendió gratamente."
        ]
        
        for usuario in usuarios:
            libros_calificados = random.sample(libros, random.randint(10, 20))
            for libro in libros_calificados:
                calificacion = Rating(
                    id_libro=libro.id_libros,
                    id_usuario=usuario.id_usuario,
                    calificacion=random.randint(3, 5),
                    resena=random.choice(reseñas_ejemplo) if random.random() > 0.4 else None
                )
                db.session.add(calificacion)
        
        db.session.commit()
        print("✓ Calificaciones creadas")
        
        print("📖 Creando bibliotecas de usuarios realistas...")
        for usuario in usuarios:
            libros_usuario = random.sample(libros, random.randint(15, 25))
            for libro in libros_usuario:
                biblioteca = UserLibrary(
                    id_libro=libro.id_libros,
                    id_usuario=usuario.id_usuario
                )
                db.session.add(biblioteca)
        
        db.session.commit()
        print("✓ Bibliotecas de usuarios creadas")
        
        print("🎉 Base de datos poblada con libros REALES!")
        print(f"   - {Admin.query.count()} administradores")
        print(f"   - {len(autores)} autores famosos")
        print(f"   - {len(libros)} libros clásicos y contemporáneos") 
        print(f"   - {len(usuarios)} usuarios de prueba")
        print(f"   - {Rating.query.count()} calificaciones")
        print(f"   - {UserLibrary.query.count()} elementos en bibliotecas")
        print("\n📚 Distribución por géneros:")
        generos_count = db.session.query(Book.genero_libro, db.func.count(Book.id_libros)).group_by(Book.genero_libro).all()
        for genero, count in generos_count:
            print(f"   - {genero}: {count} libros")

if __name__ == '__main__':
    seed_database()