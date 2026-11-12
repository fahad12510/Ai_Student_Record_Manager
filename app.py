
import json
import os
import threading
import webbrowser
from pathlib import Path

from flask import Flask, jsonify, render_template, request
from dotenv import load_dotenv

from ai_helper import analyze_performance, generate_study_tips

BASE_DIR = Path(__file__).resolve().parent
DATA_FILE = BASE_DIR / "students.json"

load_dotenv(BASE_DIR / ".env")
app = Flask(__name__)
data_lock = threading.Lock()


def load_students():
    """Load student records from the JSON file."""
    if not DATA_FILE.exists():
        save_students([])
        return []

    try:
        with DATA_FILE.open("r", encoding="utf-8") as file:
            data = json.load(file)
        if not isinstance(data, list):
            raise ValueError("The JSON file must contain a list.")
        return data
    except (json.JSONDecodeError, OSError, ValueError) as error:
        print(f"Warning: Could not load students.json: {error}")
        return []


def save_students(students):
    """Save student records with readable JSON indentation."""
    with DATA_FILE.open("w", encoding="utf-8") as file:
        json.dump(students, file, indent=4, ensure_ascii=False)


def calculate_result(marks):
    total = sum(marks.values())
    average = total / len(marks) if marks else 0

    if average >= 85:
        grade = "A"
    elif average >= 70:
        grade = "B"
    elif average >= 60:
        grade = "C"
    elif average >= 50:
        grade = "D"
    else:
        grade = "F"

    return total, round(average, 2), grade


def validate_student(data, existing_id=None):
    """Return a clean student record or raise ValueError."""
    student_id = str(data.get("id", "")).strip()
    name = str(data.get("name", "")).strip()
    student_class = str(data.get("class", "")).strip()
    subjects_text = str(data.get("subjects", "")).strip()
    marks_text = str(data.get("marks", "")).strip()

    if not all([student_id, name, student_class, subjects_text, marks_text]):
        raise ValueError("Please complete all fields.")

    students = load_students()
    for student in students:
        if student["id"].lower() == student_id.lower() and student["id"] != existing_id:
            raise ValueError("This Student ID already exists.")

    subjects = [subject.strip() for subject in subjects_text.split(",")]
    mark_values = [value.strip() for value in marks_text.split(",")]

    if any(not subject for subject in subjects) or any(not value for value in mark_values):
        raise ValueError("Subject names and marks cannot be empty.")
    if len(subjects) != len(mark_values):
        raise ValueError("The number of subjects must match the number of marks.")
    if len({subject.lower() for subject in subjects}) != len(subjects):
        raise ValueError("Subject names must not be duplicated.")

    marks = {}
    for subject, value in zip(subjects, mark_values):
        try:
            mark = float(value)
        except ValueError:
            raise ValueError(f"Marks for {subject} must be numeric.")
        if not 0 <= mark <= 100:
            raise ValueError(f"Marks for {subject} must be between 0 and 100.")
        marks[subject] = mark

    total, average, grade = calculate_result(marks)
    return {
        "id": student_id,
        "name": name,
        "class": student_class,
        "marks": marks,
        "total": total,
        "average": average,
        "grade": grade,
    }


@app.route("/")
def home():
    return render_template("index.html")


@app.route("/api/students", methods=["GET"])
def get_students():
    return jsonify(load_students())


@app.route("/api/students", methods=["POST"])
def add_student():
    try:
        student = validate_student(request.get_json(silent=True) or {})
        with data_lock:
            students = load_students()
            if any(item["id"].lower() == student["id"].lower() for item in students):
                return jsonify({"error": "This Student ID already exists."}), 400
            students.append(student)
            save_students(students)
        return jsonify({"message": "Student added successfully.", "student": student}), 201
    except ValueError as error:
        return jsonify({"error": str(error)}), 400
    except OSError:
        return jsonify({"error": "Could not save student records. Check file permissions."}), 500


@app.route("/api/students/<student_id>", methods=["PUT"])
def update_student(student_id):
    try:
        data = request.get_json(silent=True) or {}
        data["id"] = student_id
        student = validate_student(data, existing_id=student_id)
        with data_lock:
            students = load_students()
            index = next((i for i, item in enumerate(students)
                          if item["id"].lower() == student_id.lower()), None)
            if index is None:
                return jsonify({"error": "Student not found."}), 404
            students[index] = student
            save_students(students)
        return jsonify({"message": "Student updated successfully.", "student": student})
    except ValueError as error:
        return jsonify({"error": str(error)}), 400
    except OSError:
        return jsonify({"error": "Could not save student records. Check file permissions."}), 500


@app.route("/api/students/<student_id>", methods=["DELETE"])
def delete_student(student_id):
    with data_lock:
        students = load_students()
        updated = [item for item in students if item["id"].lower() != student_id.lower()]
        if len(updated) == len(students):
            return jsonify({"error": "Student not found."}), 404
        try:
            save_students(updated)
        except OSError:
            return jsonify({"error": "Could not save the updated records."}), 500
    return jsonify({"message": "Student deleted successfully."})


@app.route("/api/ai/<kind>/<student_id>", methods=["POST"])
def student_ai(kind, student_id):
    if kind not in ("analyze", "tips"):
        return jsonify({"error": "Unsupported AI request type."}), 400

    student = next((item for item in load_students()
                    if item["id"].lower() == student_id.lower()), None)
    if student is None:
        return jsonify({"error": "Student not found."}), 404

    try:
        # The AI helper receives only academic data, never the student's name or ID.
        result = (analyze_performance(student) if kind == "analyze"
                  else generate_study_tips(student))
        return jsonify({"result": result})
    except ValueError as error:
        return jsonify({"error": str(error)}), 400
    except Exception as error:
        print(f"AI request error: {error}")
        return jsonify({"error": "The AI service could not complete the request. Check your API key, model, and internet connection."}), 502


def open_browser():
    webbrowser.open("http://127.0.0.1:5000")


if __name__ == "__main__":
    # Open Chrome/default browser shortly after the local server starts.
    from threading import Timer
    if os.environ.get("WERKZEUG_RUN_MAIN") == "true" or not app.debug:
        Timer(1.2, open_browser).start()
    app.run(host="127.0.0.1", port=5000, debug=True)
