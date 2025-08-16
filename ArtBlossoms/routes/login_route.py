from flask import Blueprint, render_template, request, redirect, session
import hashlib
from db import get_db

login_bp = Blueprint('login_bp', __name__)

@login_bp.route('/login', methods=['GET', 'POST'])
def login():
    error = None
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        hashed_password = hashlib.sha256(password.encode()).hexdigest()

        conn = get_db()
        with conn.cursor() as cursor:
            cursor.execute("SELECT * FROM users WHERE username = %s", (username,))
            user = cursor.fetchone()
        conn.close()

        if user and user['password'] == hashed_password:
            if user.get('banned') == 1:
                error = "Your account has been banned."
            else:
                session['username'] = user['username']
                session['user_id'] = user['id']
                return redirect('/profile')
        else:
            error = "Invalid username or password"

    return render_template('login.html', error=error)
