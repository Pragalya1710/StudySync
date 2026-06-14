from flask import Flask, render_template, request
from flask import redirect
import mysql.connector
quiz_answers = []

app = Flask(__name__)

# MySQL Connection
db = mysql.connector.connect(
    host="localhost",
    user="root",
    password="Pragalya_1710",
    database="studysync"
)

cursor = db.cursor()

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/login', methods=['GET', 'POST'])
def login():

    if request.method == 'POST':

        email = request.form['email']
        password = request.form['password']

        sql = """
        SELECT * FROM users
        WHERE email=%s AND password=%s
        """

        values = (email, password)

        cursor.execute(sql, values)

        user = cursor.fetchone()

        if user:
            return redirect('/dashboard')
        else:
            return "Invalid Email or Password"

    return render_template('login.html')

@app.route('/register', methods=['GET', 'POST'])
def register():

    if request.method == 'POST':

        name = request.form['name']
        email = request.form['email']
        password = request.form['password']
        role = request.form['role']
        cursor.execute( "SELECT * FROM users WHERE email=%s", (email,) ) 
        existing_user = cursor.fetchone() 
        if existing_user: 
           return "Email already registered. Please login."

        sql = """
        INSERT INTO users(name,email,password,role)
        VALUES(%s,%s,%s,%s)
        """

        values = (name, email, password, role)

        cursor.execute(sql, values)
        db.commit()

        return "Registration Successful!"

    return render_template('register.html')
@app.route('/notes', methods=['GET', 'POST'])
def notes():

    if request.method == 'POST':

        title = request.form['title']
        content = request.form['content']

        sql = """
        INSERT INTO notes(user_id,title,content)
        VALUES(%s,%s,%s)
        """

        values = (1, title, content)

        cursor.execute(sql, values)
        db.commit()

        return "Note Saved Successfully!"

    return render_template('notes.html')
@app.route('/tasks', methods=['GET', 'POST'])
def tasks():

    if request.method == 'POST':

        task_name = request.form['task_name']
        deadline = request.form['deadline']
        priority = request.form['priority']

        sql = """
        INSERT INTO tasks
        (user_id, task_name, deadline, status, priority)
        VALUES(%s,%s,%s,%s,%s)
        """

        values = (
            1,
            task_name,
            deadline,
            "Pending",
            priority
        )

        cursor.execute(sql, values)
        db.commit()

        return "Task Added Successfully!"

    return render_template('tasks.html')
@app.route('/view')
def view_data():

    cursor.execute("SELECT * FROM notes")
    notes = cursor.fetchall()

    cursor.execute("SELECT * FROM tasks")
    tasks = cursor.fetchall()

    return render_template(
        'view_data.html',
        notes=notes,
        tasks=tasks
    )
@app.route('/dashboard')
def dashboard():

    cursor.execute("SELECT COUNT(*) FROM notes")
    total_notes = cursor.fetchone()[0]

    cursor.execute("SELECT COUNT(*) FROM tasks")
    total_tasks = cursor.fetchone()[0]

    cursor.execute(
        "SELECT COUNT(*) FROM tasks WHERE status='Pending'"
    )
    pending_tasks = cursor.fetchone()[0]

    cursor.execute(
        "SELECT COUNT(*) FROM tasks WHERE status='Completed'"
    )
    completed_tasks = cursor.fetchone()[0]

    return render_template(
        'dashboard.html',
        total_notes=total_notes,
        total_tasks=total_tasks,
        pending_tasks=pending_tasks,
        completed_tasks=completed_tasks
    ) 



@app.route('/progress')
def progress():

    cursor.execute("SELECT COUNT(*) FROM notes")
    total_notes = cursor.fetchone()[0]

    cursor.execute("SELECT COUNT(*) FROM tasks")
    total_tasks = cursor.fetchone()[0]

    cursor.execute(
        "SELECT COUNT(*) FROM tasks WHERE status='Pending'"
    )
    pending_tasks = cursor.fetchone()[0]

    cursor.execute(
        "SELECT COUNT(*) FROM tasks WHERE status='Completed'"
    )
    completed_tasks = cursor.fetchone()[0]

    return render_template(
        'progress.html',
        total_notes=total_notes,
        total_tasks=total_tasks,
        pending_tasks=pending_tasks,
        completed_tasks=completed_tasks
    )
@app.route('/submit_quiz', methods=['POST'])
def submit_quiz():


    score=0

    user_answers = [
    request.form.get('q1'),
    request.form.get('q2'),
    request.form.get('q3'),
    request.form.get('q4'),
    request.form.get('q5')
]

    for i in range(len(user_answers)):
       if user_answers[i] == quiz_answers[i]:
        score += 1
        
    cursor.execute(
        """
        INSERT INTO quiz_results(topic,score,total_questions)
        VALUES(%s,%s,%s)
        """,
        (topic, score, 5)
    )

    db.commit()
    

    return render_template(
    'quiz_result.html',
    score=score,
    total=5,
    answers=quiz_answers
)


@app.route('/ai', methods=['GET', 'POST'])
def ai():

    answer = ""

    if request.method == 'POST':

        question = request.form['question']

        try:

            response = client.chat.completions.create(
                model="llama-3.1-8b-instant",
                messages=[
                    {
                        "role": "system",
                        "content": "You are StudySync AI Assistant."
                    },
                    {
                        "role": "user",
                        "content": question
                    }
                ]
            )

            answer = response.choices[0].message.content

            cursor.execute(
                """
                INSERT INTO ai_history(question,answer)
                VALUES(%s,%s)
                """,
                (question, answer)
            )

            db.commit()

        except Exception as e:
            answer = str(e)

    cursor.execute("""
    SELECT * FROM ai_history
    ORDER BY id DESC
    LIMIT 10
    """)

    history = cursor.fetchall()

    return render_template(
        'ai.html',
        answer=answer,
        history=history
    )
from groq import Groq
from config import GROQ_API_KEY

client = Groq(api_key=GROQ_API_KEY)   
@app.route('/logout')
def logout():

    return redirect('/') 

@app.route('/quiz', methods=['GET', 'POST'])
def quiz():

    quiz = ""

    if request.method == 'POST':

        topic = request.form['topic']

        try:

            response = client.chat.completions.create(
                model="llama-3.1-8b-instant",
                messages=[
                    {
                        "role": "system",
                        "content": """
Create 5 multiple-choice questions.
Provide 4 options (A, B, C, D).
DO NOT show the correct answers.
Format clearly.
"""
                    },
                    {
                        "role": "user",
                        "content": f"Create a quiz on {topic}"
                    }
                ]
            )

            quiz= response.choices[0].message.content

        except Exception as e:
            quiz = str(e)

    return render_template(
        'quiz.html',
        quiz=quiz
    )



if __name__ == "__main__":
    app.run(debug=True)