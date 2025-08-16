from flask import Blueprint, render_template, request, session, redirect, url_for, flash
from db import get_db

custom_bp = Blueprint('custom_bp', __name__)

@custom_bp.route('/custom_request', methods=['GET', 'POST'])
def custom_request():
    if 'user_id' not in session:
        flash("Please login to make a custom request.")
        return redirect(url_for('login_bp.login'))

    buyer_id = session['user_id']
    artist_username = request.args.get('username')
    if not artist_username:
        flash("Invalid artist username.")
        return redirect(url_for('browse_bp.browse_artworks'))

    conn = get_db()
    with conn.cursor() as cursor:
        # Get artist info by username
        cursor.execute("SELECT id, first_name, last_name FROM users WHERE username = %s AND role IN ('artist', 'both')", (artist_username,))
        artist = cursor.fetchone()

        if not artist:
            flash("Artist not found.")
            return redirect(url_for('browse_bp.browse_artworks'))

        if request.method == 'POST':
            description = request.form.get('description', '').strip()
            if not description:
                flash("Please provide a description for your custom artwork request.")
                return render_template('custom_request.html', artist=artist, description=description)

            # Insert custom request
            cursor.execute(
                "INSERT INTO custom_requests (buyer_id, artist_id, description) VALUES (%s, %s, %s)",
                (buyer_id, artist['id'], description)
            )
            conn.commit()

            # TODO: Insert notification for artist (we'll add this in Step 3)

            flash("Custom artwork request sent successfully!")
            return redirect(url_for('profile_bp.profile'))

    conn.close()
    return render_template('custom_request.html', artist=artist)

@custom_bp.route('/custom_requests/manage')
def manage_custom_requests():
    if 'user_id' not in session:
        return redirect(url_for('login_bp.login'))

    artist_id = session['user_id']

    conn = get_db()
    with conn.cursor() as cursor:
        cursor.execute("""
            SELECT cr.id, cr.description, cr.status, u.username AS buyer_username, u.first_name, u.last_name
            FROM custom_requests cr
            JOIN users u ON cr.buyer_id = u.id
            WHERE cr.artist_id = %s
            ORDER BY cr.id DESC
        """, (artist_id,))
        requests = cursor.fetchall()

    return render_template('manage_custom_requests.html', requests=requests)

@custom_bp.route('/custom_requests/update/<int:request_id>', methods=['GET', 'POST'])
def update_custom_status(request_id):
    if 'user_id' not in session:
        return redirect(url_for('login_bp.login'))

    artist_id = session['user_id']
    conn = get_db()
    with conn.cursor() as cursor:

        # Verify artist owns the request
        cursor.execute("SELECT * FROM custom_requests WHERE id = %s AND artist_id = %s", (request_id, artist_id))
        custom_req = cursor.fetchone()
        if not custom_req:
            flash("Request not found or unauthorized access.")
            return redirect(url_for('custom_bp.manage_custom_requests'))

        if request.method == 'POST':
            new_status = request.form.get('status')
            artist_response = request.form.get('artist_response', '').strip()

            cursor.execute(
                "UPDATE custom_requests SET status = %s, artist_message = %s WHERE id = %s AND artist_id = %s",
                (new_status, artist_response, request_id, artist_id)
            )
            conn.commit()
            flash("Custom request updated successfully!")
            return redirect(url_for('custom_bp.manage_custom_requests', _external=False) + '?updated=1')


    # GET method: render the update form with current data
    return render_template('update_custom_request.html', request=custom_req)
