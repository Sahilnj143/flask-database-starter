"""
Part 4: REST API with Flask
===========================
Build a JSON API for database operations (used by frontend apps, mobile apps, etc.)

What You'll Learn:
- REST API concepts (GET, POST, PUT, DELETE)
- JSON responses with jsonify
- API error handling
- Status codes
- Testing APIs with curl or Postman

Prerequisites: Complete part-3 (SQLAlchemy)
"""
"""
Part 4: REST API with Flask (FINAL VERSION)
==========================================
Features:
- REST API (GET, POST, PUT, DELETE)
- Pagination
- Sorting
- Search & Filter
- JSON responses
- Simple frontend using fetch()
"""

from flask import Flask, request, jsonify, render_template
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

app = Flask(__name__)

# =============================================================================
# DATABASE CONFIG
# =============================================================================
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///api_demo.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

# =============================================================================
# MODEL
# =============================================================================

class Book(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    author = db.Column(db.String(100), nullable=False)
    year = db.Column(db.Integer)
    isbn = db.Column(db.String(20), unique=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def to_dict(self):
        return {
            'id': self.id,
            'title': self.title,
            'author': self.author,
            'year': self.year,
            'isbn': self.isbn,
            'created_at': self.created_at.isoformat()
        }

# =============================================================================
# REST API ROUTES
# =============================================================================

# GET (ALL) + Pagination + Sorting
@app.route('/api/books', methods=['GET'])
def get_books():
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 5, type=int)
    sort = request.args.get('sort', 'id')
    order = request.args.get('order', 'asc')

    query = Book.query

    # Sorting
    if hasattr(Book, sort):
        column = getattr(Book, sort)
        query = query.order_by(column.desc() if order == 'desc' else column.asc())

    pagination = query.paginate(page=page, per_page=per_page, error_out=False)

    return jsonify({
        'success': True,
        'page': page,
        'per_page': per_page,
        'total': pagination.total,
        'books': [book.to_dict() for book in pagination.items]
    })


# GET single book
@app.route('/api/books/<int:id>', methods=['GET'])
def get_book(id):
    book = Book.query.get(id)
    if not book:
        return jsonify({'success': False, 'error': 'Book not found'}), 404

    return jsonify({'success': True, 'book': book.to_dict()})


# POST create book
@app.route('/api/books', methods=['POST'])
def create_book():
    data = request.get_json()

    if not data or not data.get('title') or not data.get('author'):
        return jsonify({'success': False, 'error': 'Title & Author required'}), 400

    if data.get('isbn') and Book.query.filter_by(isbn=data['isbn']).first():
        return jsonify({'success': False, 'error': 'ISBN already exists'}), 400

    book = Book(
        title=data['title'],
        author=data['author'],
        year=data.get('year'),
        isbn=data.get('isbn')
    )

    db.session.add(book)
    db.session.commit()

    return jsonify({
        'success': True,
        'message': 'Book created',
        'book': book.to_dict()
    }), 201


# PUT update book
@app.route('/api/books/<int:id>', methods=['PUT'])
def update_book(id):
    book = Book.query.get(id)
    if not book:
        return jsonify({'success': False, 'error': 'Book not found'}), 404

    data = request.get_json()

    if 'title' in data:
        book.title = data['title']
    if 'author' in data:
        book.author = data['author']
    if 'year' in data:
        book.year = data['year']
    if 'isbn' in data:
        book.isbn = data['isbn']

    db.session.commit()

    return jsonify({'success': True, 'book': book.to_dict()})


# DELETE book
@app.route('/api/books/<int:id>', methods=['DELETE'])
def delete_book(id):
    book = Book.query.get(id)
    if not book:
        return jsonify({'success': False, 'error': 'Book not found'}), 404

    db.session.delete(book)
    db.session.commit()

    return jsonify({'success': True, 'message': 'Book deleted'})


# SEARCH & FILTER
@app.route('/api/books/search', methods=['GET'])
def search_books():
    query = Book.query

    title = request.args.get('q')
    author = request.args.get('author')
    year = request.args.get('year')

    if title:
        query = query.filter(Book.title.ilike(f'%{title}%'))
    if author:
        query = query.filter(Book.author.ilike(f'%{author}%'))
    if year:
        query = query.filter_by(year=int(year))

    books = query.all()

    return jsonify({
        'success': True,
        'count': len(books),
        'books': [book.to_dict() for book in books]
    })

# =============================================================================
# FRONTEND ROUTES
# =============================================================================

@app.route('/')
def home():
    return render_template('frontend.html')

# =============================================================================
# INIT DATABASE
# =============================================================================

def init_db():
    with app.app_context():
        db.create_all()

        if Book.query.count() == 0:
            books = [
                Book(title='Python Crash Course', author='Eric Matthes', year=2019),
                Book(title='Flask Web Development', author='Miguel Grinberg', year=2018),
                Book(title='Clean Code', author='Robert C. Martin', year=2008),
                Book(title='Effective Python', author='Brett Slatkin', year=2020)
            ]
            db.session.add_all(books)
            db.session.commit()
            print("Sample books inserted")

# =============================================================================
# MAIN
# =============================================================================

if __name__ == '__main__':
    init_db()
    app.run(debug=True)


# =============================================================================
# REST API CONCEPTS:
# =============================================================================
#
# HTTP Method | CRUD      | Typical Use
# ------------|-----------|---------------------------
# GET         | Read      | Retrieve data
# POST        | Create    | Create new resource
# PUT         | Update    | Update entire resource
# PATCH       | Update    | Update partial resource
# DELETE      | Delete    | Remove resource
#
# =============================================================================
# HTTP STATUS CODES:
# =============================================================================
#
# Code | Meaning
# -----|------------------
# 200  | OK (Success)
# 201  | Created
# 400  | Bad Request (client error)
# 404  | Not Found
# 500  | Internal Server Error
#
# =============================================================================
# KEY FUNCTIONS:
# =============================================================================
#
# jsonify()           - Convert Python dict to JSON response
# request.get_json()  - Get JSON data from request body
# request.args.get()  - Get query parameters (?key=value)
#
# =============================================================================
