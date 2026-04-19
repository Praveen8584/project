import os
from flask import Flask, render_template, request, redirect, session, send_file
import sqlite3
import pandas as pd
import tempfile

app = Flask(__name__)
app.secret_key = "secret123"

# DATABASE CONNECTION
def get_db():
    conn = sqlite3.connect("database.db")
    conn.row_factory = sqlite3.Row
    return conn

# CREATE TABLE
def init_db():
    conn = get_db()
    conn.execute('''CREATE TABLE IF NOT EXISTS students (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name TEXT,
                    adhar INTEGER,
                    email TEXT,
                    phone TEXT,
                    gender TEXT,
                    course TEXT
                )''')
    conn.close()

init_db()

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/login')
def user_login():
    return render_template('login.html')

@app.route('/login2')
def admin_login():
    return render_template('login2.html')

# LOGIN ADMIN
@app.route('/login2', methods=['GET', 'POST'])
def login2():
    if request.method == 'POST':
        if request.form['username'] == 'admin' and request.form['password'] == '1234':
            session['user'] = True
            return redirect('/dashboard')
    return render_template('login2.html')


# LOGIN USER
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        if request.form['username'] == 'user' and request.form['password'] == '1234':
            session['user'] = True
            return redirect('/add')
    return render_template('login.html')






# DASHBOARD
@app.route('/dashboard')
def dashboard():
    if 'user' not in session:
        return redirect('/')
    conn = get_db()
    data = conn.execute("SELECT * FROM students").fetchall()
    return render_template('dashboard.html', data=data)

# ADD STUDENT
@app.route('/add', methods=['GET', 'POST'])
def add():
    if request.method == 'POST':
        conn = get_db()
        conn.execute("INSERT INTO students (name,adhar,email,phone,gender,course) VALUES (?,?,?,?,?,?)",
                     (request.form['name'], request.form['adhar'], request.form['email'],
                      request.form['phone'], request.form['gender'],
                      request.form['course']))
        conn.commit()
        return render_template('form.html',success=True)
    return render_template('form.html',success=False)




# DELETE
@app.route('/delete/<int:id>')
def delete(id):
    conn = get_db()
    conn.execute("DELETE FROM students WHERE id=?", (id,))
    conn.commit()
    return redirect('/dashboard')

# EDIT
@app.route('/edit/<int:id>', methods=['GET', 'POST'])
def edit(id):
    conn = get_db()
    if request.method == 'POST':
        conn.execute("""UPDATE students SET name=?, adhar=?, email=?, phone=?, gender=?, course=? WHERE id=?""",
                     (request.form['name'], request.form['adhar'], request.form['email'],
                      request.form['phone'], request.form['gender'],
                      request.form['course'], id))
        conn.commit()
        return redirect('/dashboard')

    student = conn.execute("SELECT * FROM students WHERE id=?", (id,)).fetchone()
    return render_template('edit.html', student=student)

# EXPORT TO EXCEL
@app.route('/export')
def export():
    conn = get_db()
    df = pd.read_sql_query("SELECT * FROM students", conn)
    
    temp = tempfile.NamedTemporaryFile(delete=False, suffix=".xlsx")
    df.to_excel(temp.name, index=False)

    return send_file(temp.name, as_attachment=True)

# LOGOUT
@app.route('/logout')
def logout():
    session.clear()
    return redirect('/')

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)))
