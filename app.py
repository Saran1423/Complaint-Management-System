from flask import Flask, render_template, request, redirect, session
import json, os

app = Flask(__name__)
app.secret_key = "secret123"

def load_users():
    if not os.path.exists('users.json'):
        return []
    return json.load(open('users.json'))

def save_users(data):
    json.dump(data, open('users.json', 'w'), indent=4)

def load_complaints():
    if not os.path.exists('complaints.json'):
        return []
    return json.load(open('complaints.json'))

def save_complaints(data):
    json.dump(data, open('complaints.json', 'w'), indent=4)

@app.route('/', methods=['GET','POST'])
def login():
    if request.method == 'POST':
        users = load_users()
        u = request.form['username']
        p = request.form['password']

        for user in users:
            if user['username']==u and user['password']==p:
                session['user']=u
                session['role']=user['role']
                return redirect('/admin' if user['role']=="admin" else '/dashboard')

        return "Invalid Login"

    return render_template('login.html')

@app.route('/register', methods=['GET','POST'])
def register():
    if request.method == 'POST':
        users = load_users()
        users.append({
            "username":request.form['username'],
            "password":request.form['password'],
            "role":"user"
        })
        save_users(users)
        return redirect('/')
    return render_template('register.html')

@app.route('/dashboard')
def dashboard():
    if 'user' not in session:
        return redirect('/')
    complaints = load_complaints()
    user_data = [c for c in complaints if c['user']==session['user']]
    return render_template('dashboard.html', complaints=user_data)

@app.route('/add', methods=['GET','POST'])
def add():
    if 'user' not in session:
        return redirect('/')
    if request.method=='POST':
        data = load_complaints()
        data.append({
            "id":len(data)+1,
            "user":session['user'],
            "title":request.form['title'],
            "description":request.form['description'],
            "status":"Pending"
        })
        save_complaints(data)
        return redirect('/dashboard')
    return render_template('add_complaint.html')

@app.route('/admin')
def admin():
    if session.get('role')!='admin':
        return redirect('/')
    return render_template('admin.html', complaints=load_complaints())

@app.route('/update/<int:id>', methods=['POST'])
def update(id):
    data = load_complaints()
    for c in data:
        if c['id']==id:
            c['status']=request.form['status']
    save_complaints(data)
    return redirect('/admin')

@app.route('/logout')
def logout():
    session.clear()
    return redirect('/')

if __name__ == '__main__':
    app.run(debug=True)
