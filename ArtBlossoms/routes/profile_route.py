from flask import Blueprint, render_template, request, redirect, session
from werkzeug.utils import secure_filename
import os
from db import get_db

profile_bp = Blueprint('profile_bp', __name__)


@profile_bp.route('/profile', methods=['GET', 'POST'])
def profile():
    if 'username' not in session:
        return redirect('/login')

    requested_username = request.args.get('username')
    logged_in_username = session['username']
    is_own_profile = not requested_username or requested_username == logged_in_username
    username_to_show = logged_in_username if is_own_profile else requested_username

    conn = get_db()
    try:
        with conn.cursor() as cursor:
            # Get user info
            cursor.execute("SELECT * FROM users WHERE username = %s", (username_to_show,))
            user = cursor.fetchone()
            if not user:
                return "User not found", 404

            role = user['role'].strip().lower()
            user_id = user['id']

            # Determine if dashboard should be shown
            show_dashboard = role in ['artist', 'both'] and is_own_profile

            # Get artworks (for artist or both)
            artworks = []
            if role in ['artist', 'both']:
                cursor.execute("SELECT * FROM artworks WHERE user_id = %s", (user_id,))
                artworks = cursor.fetchall()

            # Get buyer orders
            buyer_orders = []
            if is_own_profile and role in ['buyer', 'both']:
                cursor.execute("""
                    SELECT o.*, a.title AS artwork_title, a.image AS artwork_image
                    FROM orders o
                    JOIN artworks a ON o.artwork_id = a.id
                    WHERE o.buyer_username = %s
                    ORDER BY o.created_at DESC
                """, (logged_in_username,))
                buyer_orders = cursor.fetchall()

            # Get custom requests (for buyers only)
            buyer_custom_requests = []
            if is_own_profile and role in ['buyer', 'both']:
                cursor.execute("""
                    SELECT cr.description, cr.status, cr.artist_response,
                           u.first_name AS artist_first, u.last_name AS artist_last, u.username AS artist_username
                    FROM custom_requests cr
                    JOIN users u ON cr.artist_id = u.id
                    WHERE cr.buyer_id = %s
                    ORDER BY cr.id DESC
                """, (user_id,))
                buyer_custom_requests = cursor.fetchall()

            # Get order notifications (for artists only)
            order_notifications = []
            if is_own_profile and role in ['artist', 'both']:
                cursor.execute("""
                    SELECT n.id, o.message, o.status, n.created_at, o.buyer_username, a.title
                    FROM order_notifications n
                    JOIN orders o ON n.order_id = o.id
                    JOIN artworks a ON o.artwork_id = a.id
                    WHERE n.artist_id = %s
                    ORDER BY n.created_at DESC
                """, (user_id,))
                order_notifications = cursor.fetchall()

            # Get report notifications
            report_notifications = []
            if is_own_profile:
                cursor.execute("""
                    SELECT id, message, is_read, created_at
                    FROM report_notifications
                    WHERE reporter_username = %s
                    ORDER BY created_at DESC
                """, (logged_in_username,))
                report_notifications = cursor.fetchall()

            # Get categories and tags
            cursor.execute("SELECT * FROM categories")
            categories = cursor.fetchall()
            cursor.execute("SELECT * FROM tags")
            tags = cursor.fetchall()

    finally:
        conn.close()

    return render_template(
        'profile.html',
        user=user,
        is_own_profile=is_own_profile,
        artworks=artworks,
        buyer_orders=buyer_orders,
        buyer_custom_requests=buyer_custom_requests,
        order_notifications=order_notifications,
        notifications=report_notifications,
        categories=categories,
        tags=tags,
        show_dashboard=show_dashboard
    )

@profile_bp.route('/upload_artwork', methods=['POST'])
def upload_artwork():
    if 'username' not in session:
        return redirect('/login')

    title = request.form['title']
    description = request.form['description']
    price = request.form['price']
    category_id = request.form['category_id']
    tag_ids = request.form.getlist('tags[]')
    art_file = request.files['art_image']

    conn = get_db()
    with conn.cursor() as cursor:
        cursor.execute("SELECT id, role FROM users WHERE username = %s", (session['username'],))
        user = cursor.fetchone()
        if not user or user['role'] not in ['artist', 'both']:
            conn.close()
            return "Unauthorized", 403
        user_id = user['id']

    filename = None
    if art_file:
        filename = secure_filename(art_file.filename)
        folder = os.path.join('static', 'uploads')
        os.makedirs(folder, exist_ok=True)
        filepath = os.path.join(folder, filename)

        count = 1
        while os.path.exists(filepath):
            name, ext = os.path.splitext(filename)
            filename = f"{name}_{count}{ext}"
            filepath = os.path.join(folder, filename)
            count += 1

        art_file.save(filepath)

    try:
        with conn.cursor() as cursor:
            cursor.execute("""
                INSERT INTO artworks (user_id, title, description, image, category_id, price)
                VALUES (%s, %s, %s, %s, %s, %s)
            """, (user_id, title, description, filename, category_id, price))
            artwork_id = cursor.lastrowid

            for tag_id in tag_ids:
                cursor.execute("INSERT INTO artwork_tags (artwork_id, tag_id) VALUES (%s, %s)", (artwork_id, tag_id))

        conn.commit()
    except Exception as e:
        conn.rollback()
        return f"Error uploading artwork: {e}", 500
    finally:
        conn.close()

    return redirect('/profile')


@profile_bp.route('/profile/bio', methods=['POST'])
def update_bio():
    if 'username' not in session:
        return redirect('/login')

    bio = request.form.get('bio', '').strip()
    username = session['username']

    conn = get_db()
    try:
        with conn.cursor() as cursor:
            cursor.execute("UPDATE users SET bio=%s WHERE username=%s", (bio, username))
        conn.commit()
    finally:
        conn.close()

    return redirect('/profile')


@profile_bp.route('/report_progress')
def report_progress():
    if 'username' not in session:
        return redirect('/login')

    username = session['username']
    conn = get_db()

    try:
        with conn.cursor() as cursor:
            cursor.execute("""
                SELECT id, message, is_read, created_at
                FROM report_notifications
                WHERE reporter_username = %s
                ORDER BY created_at DESC
            """, (username,))
            report_notifications = cursor.fetchall()

            cursor.execute("SELECT * FROM users WHERE username = %s", (username,))
            user = cursor.fetchone()

    finally:
        conn.close()

    return render_template('report_notifications.html', notifications=report_notifications, user=user)
