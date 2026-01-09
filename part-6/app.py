"""
Part 6: Homework - Product Inventory App
========================================
See Instruction.md for full requirements and hints.

How to Run:
1. Make sure venv is activated
2. Install: pip install flask flask-sqlalchemy
3. Run: python app.py
4. Open browser: http://localhost:5000
"""
import os
from flask import Flask, render_template, request, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
from dotenv import load_dotenv
from sqlalchemy.exc import OperationalError

# =================================================
# LOAD ENVIRONMENT VARIABLES
# =================================================
load_dotenv()

DATABASE_URL = os.getenv('DATABASE_URL', 'sqlite:///inventory.db')

print("📦 Using database:", DATABASE_URL)

app = Flask(__name__)
app.secret_key = os.getenv('SECRET_KEY', 'fallback-secret')

# =================================================
# DATABASE CONFIG
# =================================================
app.config['SQLALCHEMY_DATABASE_URI'] = DATABASE_URL
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Enable pooling only for PostgreSQL/MySQL
if not DATABASE_URL.startswith("sqlite"):
    app.config['SQLALCHEMY_ENGINE_OPTIONS'] = {
        'pool_size': 10,
        'pool_recycle': 3600,
        'pool_pre_ping': True
    }

db = SQLAlchemy(app)

# =================================================
# MODEL
# =================================================
class Product(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    quantity = db.Column(db.Integer, nullable=False)
    price = db.Column(db.Float, nullable=False)

# =================================================
# ROUTES
# =================================================

@app.route('/')
def index():
    try:
        products = Product.query.all()
    except OperationalError:
        products = []
    return render_template('index.html', products=products)


@app.route('/add', methods=['GET', 'POST'])
def add_product():
    if request.method == 'POST':
        product = Product(
            name=request.form['name'],
            quantity=int(request.form['quantity']),
            price=float(request.form['price'])
        )
        db.session.add(product)
        db.session.commit()
        return redirect(url_for('index'))

    return render_template('add.html')


@app.route('/delete/<int:id>')
def delete_product(id):
    product = Product.query.get_or_404(id)
    db.session.delete(product)
    db.session.commit()
    return redirect(url_for('index'))

# =================================================
# INITIALIZE DATABASE
# =================================================
def init_db():
    try:
        with app.app_context():
            db.create_all()
            print("✅ Database connected & tables created")
    except OperationalError as e:
        print("❌ Database connection failed")
        print("Reason:", e)

# =================================================
# MAIN
# =================================================
if __name__ == '__main__':
    init_db()
    app.run(debug=os.getenv('FLASK_DEBUG', 'True') == 'True')
