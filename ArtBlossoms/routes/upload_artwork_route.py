from flask import Blueprint, render_template, request, redirect, session, flash, url_for
from db import get_db
import os
from werkzeug.utils import secure_filename

upload_bp = Blueprint('upload_bp', __name__)

@upload_bp.route('/upload_artworks', methods=['GET', 'POST'])
def upload_artworks():
    if 'username' not in session:
        return redirect(url_for('login'))

    conn = get_db()
    cursor = conn.cursor()

    # Get user info
    cursor.execute("SELECT id FROM users WHERE username = %s", (session['username'],))
    user = cursor.fetchone()
    if not user:
        flash("User not found.")
        return redirect(url_for('profile'))

    artist_id = user['id']

    # Fetch categories and tags
    cursor.execute("SELECT id, name FROM categories")
    categories = cursor.fetchall()

    cursor.execute("SELECT id, name FROM tags")
    tags = cursor.fetchall()

    if request.method == 'POST':
        title = request.form['title']
        description = request.form['description']
        price = request.form['price']
        category_id = request.form['category_id']
        selected_tags = request.form.getlist('tags[]')
        art_image = request.files['art_image']

        # Save image
        filename = secure_filename(art_image.filename)
        image_path = os.path.join('static/uploads', filename)
        art_image.save(image_path)

        # Insert artwork
        cursor.execute("""
            INSERT INTO artworks (user_id, title, description, price, category_id, image)
            VALUES (%s, %s, %s, %s, %s, %s)
        """, (artist_id, title, description, price, category_id, filename))
        conn.commit()

        # Get artwork ID
        artwork_id = cursor.lastrowid

        # Insert tags
        for tag_id in selected_tags:
            cursor.execute("INSERT INTO artwork_tags (artwork_id, tag_id) VALUES (%s, %s)", (artwork_id, tag_id))
        conn.commit()

        flash("Artwork uploaded successfully.")
        return redirect(url_for('profile_bp.profile'))

    return render_template('upload_artwork_form.html', categories=categories, tags=tags)
