from flask import Blueprint, request, jsonify
from models import db, Book
from datetime import datetime
 
books_bp = Blueprint('books', __name__)
 
# 🔹 Récupérer tous les livres
@books_bp.route('/books', methods=['GET'])
def get_books():
    books = Book.query.all()
    return jsonify([
        {'id': b.id, 'title': b.title, 'author': b.author, 'published_at': b.published_at.strftime('%Y-%m-%d') if b.published_at else None}
        for b in books
    ])
 
# 🔹 Récupérer un livre par ID
@books_bp.route('/books/<int:id>', methods=['GET'])
def get_book(id):
    book = Book.query.get(id)
    if not book:
        return jsonify({'error': 'Book not found'}), 404
    return jsonify({
        'id': book.id,
        'title': book.title,
        'author': book.author,
        'published_at': book.published_at.strftime('%Y-%m-%d') if book.published_at else None
    })
 
# 🔹 Ajouter un livre
@books_bp.route('/books', methods=['POST'])
def add_book():
    data = request.get_json()
 
    if not data or 'title' not in data or 'author' not in data:
        return jsonify({'error': 'Invalid data, title and author are required'}), 400
 
    published_at = None
    if 'published_at' in data:
        try:
            published_at = datetime.strptime(data['published_at'], '%Y-%m-%d')
        except ValueError:
            return jsonify({'error': 'Invalid date format, expected YYYY-MM-DD'}), 400
 
    book = Book(title=data['title'], author=data['author'], published_at=published_at)
    db.session.add(book)
    db.session.commit()
    return jsonify({'message': 'Book added successfully', 'id': book.id}), 201
 
# 🔹 Mettre à jour un livre
@books_bp.route('/books/<int:id>', methods=['PUT'])
def update_book(id):
    book = Book.query.get(id)
    if not book:
        return jsonify({'error': 'Book not found'}), 404
 
    data = request.get_json()
    if not data:
        return jsonify({'error': 'No data provided'}), 400
 
    if 'title' in data:
        book.title = data['title']
    if 'author' in data:
        book.author = data['author']
    if 'published_at' in data:
        try:
            book.published_at = datetime.strptime(data['published_at'], '%Y-%m-%d')
        except ValueError:
            return jsonify({'error': 'Invalid date format, expected YYYY-MM-DD'}), 400
 
    db.session.commit()
    return jsonify({'message': 'Book updated successfully'})
 
# 🔹 Supprimer un livre
@books_bp.route('/books/<int:id>', methods=['DELETE'])
def delete_book(id):
    book = Book.query.get(id)
    if not book:
        return jsonify({'error': 'Book not found'}), 404
 
    db.session.delete(book)
    db.session.commit()
    return jsonify({'message': 'Book deleted successfully'})
 
# 🔹 Endpoint pour emprunter un livre
@books_bp.route('/books/<int:book_id>/borrow', methods=['POST'])
def borrow_book(book_id):
    data = request.get_json()
 
    # Vérifie que student_id est bien fourni
    if not data or 'student_id' not in data:
        return jsonify({'error': 'student_id is required'}), 400
 
    student_id = data['student_id']
 
    # Vérifie si le livre existe
    book = Book.query.get(book_id)
    if not book:
        return jsonify({'error': 'Book not found'}), 404
 
    # Vérifie si l'étudiant existe
    from models import Student, StudentBook
    student = Student.query.get(student_id)
    if not student:
        return jsonify({'error': 'Student not found'}), 404
 
    # Crée un enregistrement d'emprunt avec la date actuelle
    borrow = StudentBook(student_id=student_id, book_id=book_id, borrow_date=datetime.utcnow())
    db.session.add(borrow)
    db.session.commit()
 
    return jsonify({'message': 'Book borrowed successfully'}), 201
 
# 🔹 Endpoint pour rendre un livre
@books_bp.route('/books/<int:book_id>/return', methods=['POST'])
def return_book(book_id):
    data = request.get_json()
 
    # Vérifie que student_id est fourni
    if not data or 'student_id' not in data:
        return jsonify({'error': 'student_id is required'}), 400
 
    student_id = data['student_id']
 
    # Vérifie si le livre existe
    book = Book.query.get(book_id)
    if not book:
        return jsonify({'error': 'Book not found'}), 404
 
    # Vérifie si l'étudiant existe
    from models import Student, StudentBook
    student = Student.query.get(student_id)
    if not student:
        return jsonify({'error': 'Student not found'}), 404
 
    # Recherche de l'enregistrement d'emprunt actif (non rendu)
    borrow = StudentBook.query.filter_by(student_id=student_id, book_id=book_id, return_date=None).first()
    if not borrow:
        return jsonify({'error': 'No active borrow record found for this student and book'}), 404
 
    # Marque le livre comme rendu (date de retour = maintenant)
    borrow.return_date = datetime.utcnow()
    db.session.commit()
 
    return jsonify({'message': 'Book returned successfully'}), 200
 