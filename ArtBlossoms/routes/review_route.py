from flask import Blueprint, render_template, request, redirect, session, flash, url_for
from db import get_db

review_bp = Blueprint('review_bp', __name__)

@review_bp.route('/review/<int:artwork_id>', methods=['GET', 'POST'])
def review_artwork(artwork_id):
    if 'username' not in session:
        return redirect(url_for('login'))

    username = session['username']
    conn = get_db()
    try:
        with conn.cursor() as cursor:
            # Get buyer's ID
            cursor.execute("SELECT id FROM users WHERE username = %s", (username,))
            buyer = cursor.fetchone()
            if not buyer:
                flash("User not found.")
                return redirect(url_for('profile_bp.profile'))

            buyer_id = buyer['id']

            # Check if the artwork was delivered to this buyer
            cursor.execute("""
                SELECT * FROM orders 
                WHERE artwork_id = %s AND buyer_username = %s AND status = 'Sent to Delivery'
            """, (artwork_id, username))
            order = cursor.fetchone()
            if not order:
                flash("You can only review an artwork after it's marked as delivered.")
                return redirect(url_for('profile_bp.profile'))

            # If POST: save the review
            if request.method == 'POST':
                rating = int(request.form['rating'])
                comment = request.form['comment']

                cursor.execute("""
                    INSERT INTO reviews (artwork_id, buyer_id, rating, comment)
                    VALUES (%s, %s, %s, %s)
                """, (artwork_id, buyer_id, rating, comment))
                conn.commit()

                flash("Thanks for reviewing the artwork!")
                return redirect(url_for('profile_bp.profile'))

            # For GET: load artwork title for display
            cursor.execute("SELECT title FROM artworks WHERE id = %s", (artwork_id,))
            artwork = cursor.fetchone()
    finally:
        conn.close()

    return render_template('review_form.html', artwork=artwork, artwork_id=artwork_id)