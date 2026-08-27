from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from models import db, ReadingBook

books_bp = Blueprint('books', __name__, url_prefix='/api')

@books_bp.route('/books', methods=['GET'])
@jwt_required()
def get_books():
    user_id = int(get_jwt_identity())
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 10, type=int)

    # Return only the authenticated user's reading list, with pagination.
    pagination = ReadingBook.query.filter_by(user_id=user_id)\
        .order_by(ReadingBook.updated_at.desc())\
        .paginate(page=page, per_page=per_page, error_out=False)

    books = [{
        "id": b.id,
        "openlibrary_id": b.openlibrary_id,
        "title": b.title,
        "author": b.author,
        "cover_url": b.cover_url,
        "status": b.status,
        "rating": b.rating
    } for b in pagination.items]

    return jsonify({
        "books": books,
        "total": pagination.total,
        "page": page,
        "per_page": per_page,
        "pages": pagination.pages
    }), 200

def normalize_status(status):
    if status in ('want_to_read', 'want to read'):
        return 'want-to-read'
    if status in ('currently_reading', 'reading'):
        return 'reading'
    if status == 'read':
        return 'read'
    return 'want-to-read'


@books_bp.route('/books', methods=['POST'])
@jwt_required()
def create_book():
    user_id = int(get_jwt_identity())
    data = request.get_json() or {}

    new_book = ReadingBook(
        user_id=user_id,
        openlibrary_id=data.get('openlibrary_id'),
        title=data.get('title'),
        author=data.get('author'),
        cover_url=data.get('cover_url'),
        status=normalize_status(data.get('status', 'want-to-read')),
        rating=data.get('rating')
    )
    db.session.add(new_book)
    db.session.commit()
    db.session.refresh(new_book)
    
    return jsonify({"id": new_book.id, "title": new_book.title, "status": new_book.status}), 201

@books_bp.route('/books/<int:book_id>', methods=['PATCH'])
@jwt_required()
def update_book(book_id):
    user_id = int(get_jwt_identity())
    book = ReadingBook.query.get_or_404(book_id)

    # Users can only modify entries that belong to their own reading list.
    if book.user_id != user_id:
        return jsonify({"error": "Forbidden: You do not own this book record"}), 403

    data = request.get_json() or {}
    if 'status' in data:
        book.status = normalize_status(data['status'])
    if 'rating' in data:
        book.rating = data['rating']

    db.session.commit()
    return jsonify({"id": book.id, "status": book.status, "rating": book.rating}), 200

@books_bp.route('/books/<int:book_id>', methods=['DELETE'])
@jwt_required()
def delete_book(book_id):
    user_id = int(get_jwt_identity())
    book = ReadingBook.query.get_or_404(book_id)

    if book.user_id != user_id:
        return jsonify({"error": "Forbidden: You do not own this book record"}), 403

    db.session.delete(book)
    db.session.commit()
    return jsonify({"message": "Book removed successfully"}), 200