from flask import Flask, request, render_template_string, redirect, session
import sqlite3


# Vulnerablities SQL Injection:
#
# Username:  ' OR '1'='1
# Password:  ' OR '1'='1
# 
# For the rest, use the following credentials:
# 
# Username: admin
# Password: adminpass
#
# Go to the Bug Report Tab and enter in the following: <script>alert("XSS success!")</script>
# Click Submit
# You should see the alert box pop up - the Java Script code is executed
# 
# You can also open this link to see everyone who has logged in: http://localhost:5000/api/users
# 
# Go again to the Bug Report Tab and enter in the following: <b>Nice bold bug</b>
# Click Submit
# You should see the bold text in the bug feed
# 




app = Flask(__name__)
app.secret_key = 'insecurekey'  # ⚠️ Insecure hardcoded secret

# --- DB Setup ---
def init_db():
    conn = sqlite3.connect('bugs.db')
    c = conn.cursor()
    c.execute('CREATE TABLE IF NOT EXISTS users (username TEXT, password TEXT)')
    c.execute('CREATE TABLE IF NOT EXISTS bugs (report TEXT, reporter TEXT)')
    c.execute("INSERT OR IGNORE INTO users VALUES ('admin', 'adminpass')")
    conn.commit()
    conn.close()

init_db()

# --- Home Route ---
@app.route('/')
def home():
    if 'user' in session:
        return render_template_string('''
        <html>
        <head><link rel="stylesheet" href="/static/style.css"></head>
        <body>
          <p>Logged in as {{user}}</p>
          <a href="/report">Report Bug</a> | <a href="/bugs">View Bugs</a> | <a href="/logout">Logout</a>
        </body>
        </html>
        ''', user=session['user'])
    return render_template_string('''
    <html>
    <head><link rel="stylesheet" href="/static/style.css"></head>
    <body>
      <a href="/login">Login</a>
    </body>
    </html>
    ''')

# --- Login Route (Vulnerable to SQLi) ---
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        user = request.form['username']
        pw = request.form['password']
        conn = sqlite3.connect('bugs.db')
        c = conn.cursor()
        query = f"SELECT * FROM users WHERE username='{user}' AND password='{pw}'"  # ⚠️ SQLi
        result = c.execute(query).fetchone()
        if result:
            session['user'] = user
            return redirect('/')
        return "Login failed"

    return render_template_string('''
    <html>
    <head><link rel="stylesheet" href="/static/style.css"></head>
    <body>
      <h2>Login</h2>
      <form method="post">
        <input name="username" placeholder="Username"><br>
        <input name="password" type="password" placeholder="Password"><br>
        <button>Login</button>
      </form>
      <a href="/">Back to Home</a>
    </body>
    </html>
    ''')

# --- Bug Report Route (Stored XSS vulnerability) ---
@app.route('/report', methods=['GET', 'POST'])
def report():
    if 'user' not in session:
        return redirect('/login')

    if request.method == 'POST':
        bug = request.form['bug']
        reporter = session['user']
        conn = sqlite3.connect('bugs.db')
        c = conn.cursor()
        c.execute("INSERT INTO bugs VALUES (?, ?)", (bug, reporter))  # ⚠️ No XSS filtering
        conn.commit()
        return redirect('/bugs')

    return render_template_string('''
    <html>
    <head><link rel="stylesheet" href="/static/style.css"></head>
    <body>
      <h2>Submit Bug Report</h2>
      <form method="post">
        <textarea name="bug" placeholder="Describe the bug..."></textarea><br>
        <button>Submit</button>
      </form>
      <a href="/">Back to Home</a>
    </body>
    </html>
    ''')

# --- View Bugs (shows stored XSS) ---
@app.route('/bugs')
def bugs():
    conn = sqlite3.connect('bugs.db')
    c = conn.cursor()
    bugs = c.execute("SELECT * FROM bugs").fetchall()

    # Generate bug list with no XSS protection
    output = "<html><head><link rel='stylesheet' href='/static/style.css'></head><body>"
    output += "<h2>Bug Feed</h2>"
    for bug in bugs:
        output += f"<p><b>{bug[1]}</b>: {bug[0]}</p>"
    output += "<a href='/'>Back to Home</a></body></html>"
    return output

# --- Logout Route ---
@app.route('/logout')
def logout():
    session.clear()
    return redirect('/')

# --- Insecure API Route (No Auth) ---
@app.route('/api/users')
def api_users():
    conn = sqlite3.connect('bugs.db')
    c = conn.cursor()
    users = c.execute("SELECT * FROM users").fetchall()
    return {'users': users}  # ⚠️ Sensitive data exposed

if __name__ == "__main__":
    app.run(debug=True)
