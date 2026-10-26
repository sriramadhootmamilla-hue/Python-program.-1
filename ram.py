\https://your-student-system.example.com```

All users will access the same database.

## Example Flask backend using SQLite

This is a basic replacement for your current JSON-based class:

```python
from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

app = Flask(__name__)

app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///students.db"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

db = SQLAlchemy(app)


class Student(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    full_name = db.Column(db.String(150), nullable=False)
    email = db.Column(db.String(150), nullable=False, unique=True)
    phone = db.Column(db.String(50), nullable=False)
    dob = db.Column(db.String(20), nullable=False)
    program = db.Column(db.String(150), nullable=False)
    year_level = db.Column(db.String(50), nullable=False)
    address = db.Column(db.Text, nullable=False)
    date_registered = db.Column(
        db.DateTime,
        default=datetime.utcnow
    )

    def to_dict(self):
        return {
            "id": self.id,
            "fullName": self.full_name,
            "email": self.email,
            "phone": self.phone,
            "dob": self.dob,
            "program": self.program,
            "yearLevel": self.year_level,
            "address": self.address,
            "dateRegistered": self.date_registered.isoformat()
        }


@app.route("/api/students", methods=["GET"])
def get_students():
    query = request.args.get("search", "").strip()

    if query:
        students = Student.query.filter(
            db.or_(
                Student.full_name.ilike(f"%{query}%"),
                Student.email.ilike(f"%{query}%")
            )
        ).all()
    else:
        students = Student.query.all()

    return jsonify([student.to_dict() for student in students])


@app.route("/api/students", methods=["POST"])
def add_student():
    data = request.get_json()

    required_fields = [
        "fullName",
        "email",
        "phone",
        "dob",
        "program",
        "yearLevel",
        "address"
    ]

    missing_fields = [
        field for field in required_fields
        if not data.get(field)
    ]

    if missing_fields:
        return jsonify({
            "error": "Missing required fields",
            "fields": missing_fields
        }), 400

    existing_student = Student.query.filter_by(
        email=data["email"]
    ).first()

    if existing_student:
        return jsonify({
            "error": "A student with this email already exists"
        }), 409

    student = Student(
        full_name=data["fullName"],
        email=data["email"],
        phone=data["phone"],
        dob=data["dob"],
        program=data["program"],
        year_level=data["yearLevel"],
        address=data["address"]
    )

    db.session.add(student)
    db.session.commit()

    return jsonify(student.to_dict()), 201


@app.route("/api/students/<int:student_id>", methods=["GET"])
def get_student(student_id):
    student = db.session.get(Student, student_id)

    if not student:
        return jsonify({"error": "Student not found"}), 404

    return jsonify(student.to_dict())


@app.route("/api/students/<int:student_id>", methods=["PUT"])
def update_student(student_id):
    student = db.session.get(Student, student_id)

    if not student:
        return jsonify({"error": "Student not found"}), 404

    data = request.get_json()

    field_mapping = {
        "fullName": "full_name",
        "email": "email",
        "phone": "phone",
        "dob": "dob",
        "program": "program",
        "yearLevel": "year_level",
        "address": "address"
    }

    for request_field, model_field in field_mapping.items():
        if request_field in data:
            setattr(student, model_field, data[request_field])

    db.session.commit()

    return jsonify(student.to_dict())


@app.route("/api/students/<int:student_id>", methods=["DELETE"])
def delete_student(student_id):
    student = db.session.get(Student, student_id)

    if not student:
        return jsonify({"error": "Student not found"}), 404

    db.session.delete(student)
    db.session.commit()

    return jsonify({
        "message": "Student deleted successfully"
    })


with app.app_context():
    db.create_all()


if __name__ == "__main__":
    app.run(debug=True)
