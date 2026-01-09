"""
Part 3: Flask-SQLAlchemy ORM
============================
Say goodbye to raw SQL! Use Python classes to work with databases.

What You'll Learn:
- Setting up Flask-SQLAlchemy
- Creating Models (Python classes = database tables)
- ORM queries instead of raw SQL
- Relationships between tables (One-to-Many)

Prerequisites: Complete part-1 and part-2
Install: pip install flask-sqlalchemy
"""
from flask import Flask, render_template, request, redirect, url_for, flash
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.secret_key = 'your-secret-key'

# =============================================================================
# DATABASE CONFIGURATION
# =============================================================================
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///school.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

# =============================================================================
# MODELS
# =============================================================================

# ---------------- TEACHER MODEL ----------------
class Teacher(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)

    # One teacher -> many courses
    courses = db.relationship('Course', backref='teacher', lazy=True)

    def __repr__(self):
        return f'<Teacher {self.name}>'


# ---------------- COURSE MODEL ----------------
class Course(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text)

    teacher_id = db.Column(db.Integer, db.ForeignKey('teacher.id'), nullable=False)

    # One course -> many students
    students = db.relationship('Student', backref='course', lazy=True)

    def __repr__(self):
        return f'<Course {self.name}>'


# ---------------- STUDENT MODEL ----------------
class Student(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)

    course_id = db.Column(db.Integer, db.ForeignKey('course.id'), nullable=False)

    def __repr__(self):
        return f'<Student {self.name}>'


# =============================================================================
# ROUTES
# =============================================================================

# ---------------- HOME / STUDENTS LIST ----------------
@app.route('/')
def index():
    students = Student.query.order_by(Student.id.desc()).all()
    return render_template('index.html', students=students)


# ---------------- COURSES LIST ----------------
@app.route('/courses')
def courses():
    courses = Course.query.all()
    return render_template('courses.html', courses=courses)


# ---------------- ADD STUDENT ----------------
@app.route('/add', methods=['GET', 'POST'])
def add_student():
    courses = Course.query.all()

    if request.method == 'POST':
        name = request.form['name']
        email = request.form['email']
        course_id = request.form['course_id']

        # Email validation
        if Student.query.filter_by(email=email).first():
            flash('Email already exists!', 'danger')
            return redirect(url_for('add_student'))

        student = Student(name=name, email=email, course_id=course_id)
        db.session.add(student)
        db.session.commit()

        flash('Student added successfully!', 'success')
        return redirect(url_for('index'))

    return render_template('add.html', courses=courses)


# ---------------- EDIT STUDENT ----------------
@app.route('/edit/<int:id>', methods=['GET', 'POST'])
def edit_student(id):
    student = Student.query.get_or_404(id)
    courses = Course.query.all()

    if request.method == 'POST':
        student.name = request.form['name']
        student.email = request.form['email']
        student.course_id = request.form['course_id']

        db.session.commit()
        flash('Student updated successfully!', 'success')
        return redirect(url_for('index'))

    return render_template('edit.html', student=student, courses=courses)


# ---------------- DELETE STUDENT ----------------
@app.route('/delete/<int:id>')
def delete_student(id):
    student = Student.query.get_or_404(id)
    db.session.delete(student)
    db.session.commit()

    flash('Student deleted!', 'danger')
    return redirect(url_for('index'))


# ---------------- ADD COURSE ----------------
@app.route('/add-course', methods=['GET', 'POST'])
def add_course():
    teachers = Teacher.query.all()

    if request.method == 'POST':
        name = request.form['name']
        description = request.form.get('description', '')
        teacher_id = request.form['teacher_id']

        course = Course(name=name, description=description, teacher_id=teacher_id)
        db.session.add(course)
        db.session.commit()

        flash('Course added successfully!', 'success')
        return redirect(url_for('courses'))

    return render_template('add_course.html', teachers=teachers)


# =============================================================================
# DATABASE INITIALIZATION
# =============================================================================

def init_db():
    with app.app_context():
        db.create_all()

        # Add teachers
        if Teacher.query.count() == 0:
            teachers = [
                Teacher(name='Mr. Sharma', email='sharma@school.com'),
                Teacher(name='Ms. Patil', email='patil@school.com')
            ]
            db.session.add_all(teachers)
            db.session.commit()

        # Add courses
        if Course.query.count() == 0:
            courses = [
                Course(name='Python Basics', description='Python fundamentals', teacher_id=1),
                Course(name='Web Development', description='Flask & Web Tech', teacher_id=2),
                Course(name='Data Science', description='Data analysis', teacher_id=1)
            ]
            db.session.add_all(courses)
            db.session.commit()


# =============================================================================
# MAIN
# =============================================================================
if __name__ == '__main__':
    init_db()
    app.run(debug=True)

# =============================================================================
# ORM vs RAW SQL COMPARISON:
# =============================================================================
#
# Operation      | Raw SQL                          | SQLAlchemy ORM
# ---------------|----------------------------------|---------------------------
# Get all        | SELECT * FROM students           | Student.query.all()
# Get by ID      | SELECT * WHERE id = ?            | Student.query.get(id)
# Filter         | SELECT * WHERE name = ?          | Student.query.filter_by(name='John')
# Insert         | INSERT INTO students VALUES...   | db.session.add(student)
# Update         | UPDATE students SET...           | student.name = 'New'; db.session.commit()
# Delete         | DELETE FROM students WHERE...    | db.session.delete(student)
#
# =============================================================================
# COMMON QUERY METHODS:
# =============================================================================
#
# Student.query.all()                    - Get all records
# Student.query.first()                  - Get first record
# Student.query.get(1)                   - Get by primary key
# Student.query.get_or_404(1)            - Get or show 404 error
# Student.query.filter_by(name='John')   - Filter by exact value
# Student.query.filter(Student.name.like('%john%'))  - Filter with LIKE
# Student.query.order_by(Student.name)   - Order results
# Student.query.count()                  - Count records
#
# =============================================================================
