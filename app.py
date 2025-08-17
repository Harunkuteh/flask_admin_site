from flask import Flask, render_template, request, redirect, session, url_for
import sqlite3

app = Flask(__name__)
app.secret_key = 'secret_key123'  # ใช้สำหรับ session

def get_db_connection():
    conn = sqlite3.connect('database.db')
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    conn = get_db_connection()
    c = conn.cursor()
    # สร้างตาราง admin
    c.execute('''CREATE TABLE IF NOT EXISTS admin (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    username TEXT NOT NULL,
                    password TEXT NOT NULL)''')
    # สร้างตาราง content
    c.execute('''CREATE TABLE IF NOT EXISTS content (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    title TEXT,
                    body TEXT)''')
    # เพิ่ม admin เริ่มต้นถ้ายังไม่มี
    c.execute("SELECT * FROM admin WHERE username='admin'")
    if not c.fetchone():
        c.execute("INSERT INTO admin (username, password) VALUES (?, ?)", ('admin', 'admin123'))
    conn.commit()
    conn.close()

@app.route('/')
def home():
    conn = get_db_connection()
    contents = conn.execute('SELECT * FROM content').fetchall()
    conn.close()
    return render_template('home.html', content=contents)

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        user = request.form['username']
        pw = request.form['password']
        conn = get_db_connection()
        admin = conn.execute('SELECT * FROM admin WHERE username=? AND password=?', (user, pw)).fetchone()
        conn.close()
        if admin:
            session['admin'] = user
            return redirect(url_for('dashboard'))
        else:
            return render_template('login.html', error="ชื่อผู้ใช้หรือรหัสผ่านไม่ถูกต้อง")
    return render_template('login.html')

@app.route('/dashboard')
def dashboard():
    if 'admin' not in session:
        return redirect(url_for('login'))
    conn = get_db_connection()
    contents = conn.execute('SELECT * FROM content').fetchall()
    conn.close()
    return render_template('dashboard.html', content=contents)

@app.route('/add', methods=['POST'])
def add():
    if 'admin' not in session:
        return redirect(url_for('login'))
    title = request.form['title']
    body = request.form['body']
    conn = get_db_connection()
    conn.execute('INSERT INTO content (title, body) VALUES (?, ?)', (title, body))
    conn.commit()
    conn.close()
    return redirect(url_for('dashboard'))

@app.route('/delete/<int:id>')
def delete(id):
    if 'admin' not in session:
        return redirect(url_for('login'))
    conn = get_db_connection()
    conn.execute('DELETE FROM content WHERE id=?', (id,))
    conn.commit()
    conn.close()
    return redirect(url_for('dashboard'))

@app.route('/edit/<int:id>', methods=['GET', 'POST'])
def edit(id):
    if 'admin' not in session:
        return redirect(url_for('login'))
    conn = get_db_connection()
    if request.method == 'POST':
        title = request.form['title']
        body = request.form['body']
        conn.execute('UPDATE content SET title=?, body=? WHERE id=?', (title, body, id))
        conn.commit()
        conn.close()
        return redirect(url_for('dashboard'))
    else:
        content = conn.execute('SELECT * FROM content WHERE id=?', (id,)).fetchone()
        conn.close()
        if content is None:
            return "ไม่พบเนื้อหา", 404
        return render_template('edit.html', content=content)

@app.route('/logout')
def logout():
    session.pop('admin', None)
    return redirect(url_for('home'))

if __name__ == '__main__':
    init_db()
    app.run(debug=True)
