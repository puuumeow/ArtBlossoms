from flask import Blueprint, render_template, request, redirect, current_app
import os
import hashlib
from werkzeug.utils import secure_filename
from db import get_db

register_bp = Blueprint('register_bp', __name__)

@register_bp.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        first = request.form['first_name']
        last = request.form['last_name']
        username = request.form['username']
        email = request.form['email']
        mobile = request.form['mobile']
        role = request.form['role']
        password = request.form['password']

        hashed_password = hashlib.sha256(password.encode()).hexdigest()

        file = request.files['profile_pic']
        if file:
            filename = secure_filename(file.filename)
            upload_folder = current_app.config['UPLOAD_FOLDER']
            os.makedirs(upload_folder, exist_ok=True)

            filepath = os.path.join(upload_folder, filename)
            count = 1
            while os.path.exists(filepath):
                name, ext = os.path.splitext(filename)
                filename = f"{name}_{count}{ext}"
                filepath = os.path.join(upload_folder, filename)
                count += 1
            file.save(filepath)
        else:
            filename = None

        conn = get_db()
        try:
            with conn.cursor() as cursor:
                cursor.execute("SELECT * FROM users WHERE username=%s OR email=%s", (username, email))
                existing = cursor.fetchone()
                if existing:
                    conn.close()
                    return "Username or Email already registered. Please try another.", 400

                cursor.execute("""
                    INSERT INTO users 
                    (first_name, last_name, username, email, mobile, role, profile_pic, password)
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
                """, (first, last, username, email, mobile, role, filename, hashed_password))
                conn.commit()
        except Exception as e:
            conn.close()
            return f"Database error: {str(e)}", 500

        conn.close()
        return redirect('/login')

    return render_template('register.html')
