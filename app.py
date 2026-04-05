from flask import Flask, render_template, request, redirect, session
import json
import os

app = Flask(__name__)
app.secret_key = "secret"

# Load JSON safely
def load_users():
    if not os.path.exists('users.json'):
        return []
    with open('users.json', 'r') as f:
        return json.load(f)

def load_complaints():
    if not os.path.exists('complaints.json'):
        return []
    with open('complaints.json', 'r') as f:
        return json.load(f)

def save_complaints(data):
    with open('complaints.json', 'w') as f:
        json.dump(data, f, indent=4)

def save_users(data):
    with open('users.json', 'w') as f:
        json.dump(data, f, indent=4)

# ---------------- ROUTES ---------------- #

@app.route('/', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        users = load_users()
        username = request.form['username']
        password = request.form['password']

        for user in users:
            if user['username'] == username and user['password'] == password:
                session['user'] = username
                session['role'] = user['role']

                if user['role'] == 'admin':
                    return redirect('/admin')
                return redirect('/dashboard')

        return "Invalid Credentials"

    return render_template('login.html')


@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        users = load_users()

        users.append({
            "username": request.form['username'],
            "password": request.form['password'],
            "role": "user"
        })

        save_users(users)
        return redirect('/')

    return render_template('register.html')


@app.route('/dashboard')
def dashboard():
    if 'user' not in session:
        return redirect('/')

    complaints = load_complaints()
    user_complaints = [c for c in complaints if c['user'] == session['user']]

    return render_template('dashboard.html', complaints=user_complaints)


@app.route('/add', methods=['GET', 'POST'])
def add():
    if 'user' not in session:
        return redirect('/')

    if request.method == 'POST':
        complaints = load_complaints()

        complaints.append({
            "id": len(complaints) + 1,
            "user": session['user'],
            "title": request.form['title'],
            "description": request.form['description'],
            "status": "Pending"
        })

        save_complaints(complaints)
        return redirect('/dashboard')

    return render_template('add_complaint.html')


@app.route('/admin')
def admin():
    if 'role' not in session or session['role'] != 'admin':
        return redirect('/')

    complaints = load_complaints()
    return render_template('admin.html', complaints=complaints)


@app.route('/update/<int:id>', methods=['POST'])
def update(id):
    complaints = load_complaints()

    for c in complaints:
        if c['id'] == id:
            c['status'] = request.form['status']

    save_complaints(complaints)
    return redirect('/admin')


@app.route('/logout')
def logout():
    session.clear()
    return redirect('/')


# Run app
if __name__ == '__main__':
    app.run(debug=True)