import os
import json
import random
import sqlite3
from flask import Flask, render_template, request

app = Flask(__name__)

def load_questions():
    with open("questions.json", "r", encoding="utf-8") as f:
        return json.load(f)

def init_db():
    conn = sqlite3.connect("answers.db")
    c = conn.cursor()

    c.execute("""
    CREATE TABLE IF NOT EXISTS quiz_results(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        student_name TEXT,
        score INTEGER,
        total INTEGER
    )
    """)

    c.execute("""
    CREATE TABLE IF NOT EXISTS quiz_answers(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        student_name TEXT,
        question_text TEXT,
        selected_answer TEXT,
        correct_answer TEXT,
        is_correct INTEGER
    )
    """)

    conn.commit()
    conn.close()

@app.route("/", methods=["GET", "POST"])
def index():
    questions = load_questions()

    if request.method == "POST":
        student_name = request.form["name"].strip()

        if not student_name:
            return "Ad soyad boş bırakılamaz."

        selected_questions = random.sample(questions, 5)
        return render_template(
            "index.html",
            student_name=student_name,
            questions=selected_questions
        )

    return render_template("index.html", questions=None)

@app.route("/submit_quiz", methods=["POST"])
def submit_quiz():
    student_name = request.form["student_name"].strip()
    questions = load_questions()

    question_map = {str(q["id"]): q for q in questions}

    score = 0
    saved_answers = []

    for key in request.form:
        if key.startswith("question_"):
            qid = key.replace("question_", "")
            selected = request.form.get(key)
            q = question_map.get(qid)

            if q:
                correct = q["answer"]
                is_correct = 1 if selected == correct else 0
                score += is_correct

                saved_answers.append((
                    student_name,
                    q["text"],
                    selected,
                    correct,
                    is_correct
                ))

    conn = sqlite3.connect("answers.db")
    c = conn.cursor()

    c.execute(
        "INSERT INTO quiz_results(student_name, score, total) VALUES (?, ?, ?)",
        (student_name, score, 5)
    )

    c.executemany("""
    INSERT INTO quiz_answers(
        student_name,
        question_text,
        selected_answer,
        correct_answer,
        is_correct
    )
    VALUES (?, ?, ?, ?, ?)
    """, saved_answers)

    conn.commit()
    conn.close()

    return render_template(
        "success.html",
        student_name=student_name,
        score=score,
        total=5
    )

@app.route("/admin")
def admin():
    conn = sqlite3.connect("answers.db")
    c = conn.cursor()

    c.execute("""
    SELECT id, student_name, score, total
    FROM quiz_results
    ORDER BY id DESC
    """)
    results = c.fetchall()

    c.execute("""
    SELECT student_name, question_text, selected_answer, correct_answer, is_correct
    FROM quiz_answers
    ORDER BY id DESC
    """)
    answers = c.fetchall()

    conn.close()

    return render_template("admin.html", results=results, answers=answers)

if __name__ == "__main__":
    init_db()
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)))