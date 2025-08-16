from flask import Blueprint, render_template, session, abort, request, redirect, url_for
from db import get_db
import pymysql.cursors  # Needed for DictCursor

artwork_bp = Blueprint('artwork_bp', __name__)

@artwork_bp.route('/artwork/<int:artwork_id>')
def artwork_detail(artwork_id):
    conn = get_db()
    try:
        with conn.cursor(pymysql.cursors.DictCursor) as cursor:
            # Fetch artwork info with artist & category
            cursor.execute("""
                SELECT a.*, u.username, u.first_name, u.last_name, c.name AS category_name
                FROM artworks a
                JOIN users u ON a.user_id = u.id
                JOIN categories c ON a.category_id = c.id
                WHERE a.id = %s
            """, (artwork_id,))
            artwork = cursor.fetchone()
            if not artwork:
                abort(404, description="Artwork not found")

            # Fetch tags
            cursor.execute("""
                SELECT t.name
                FROM tags t
                JOIN artwork_tags at ON t.id = at.tag_id
                WHERE at.artwork_id = %s
            """, (artwork_id,))
            tags = [row['name'] for row in cursor.fetchall()]

            # If not logged in, show guest version
            if 'username' not in session:
                return render_template('artwork_guest_view.html', artwork=artwork, tags=tags)

            # Fetch reviews for artwork
            cursor.execute("""
                SELECT r.*, u.first_name, u.last_name
                FROM reviews r
                JOIN users u ON r.buyer_id = u.id
                WHERE r.artwork_id = %s
                ORDER BY r.created_at DESC
            """, (artwork_id,))
            reviews = cursor.fetchall()

            # Get current user info
            cursor.execute("SELECT * FROM users WHERE username = %s", (session['username'],))
            user = cursor.fetchone()

            # Check if user can leave a review (has an order with status 'Sent to Delivery')
            can_review = False
            cursor.execute("""
                SELECT COUNT(*) AS count
                FROM orders o
                WHERE o.artwork_id = %s
                  AND o.buyer_username = %s
                  AND o.status = 'Sent to Delivery'
            """, (artwork_id, session['username']))
            result = cursor.fetchone()
            if result and result['count'] > 0:
                can_review = True

        return render_template(
            'artwork_detail.html',
            artwork=artwork,
            tags=tags,
            reviews=reviews,
            user=user,
            can_review=can_review
        )
    finally:
        conn.close()

        
from flask import Blueprint, render_template, session, abort
from db import get_db
import pymysql.cursors  # Needed for DictCursor

artwork_bp = Blueprint('artwork_bp', __name__)

@artwork_bp.route('/artwork/<int:artwork_id>')
def artwork_detail(artwork_id):
    conn = get_db()
    try:
        # Use DictCursor for convenient key-based access
        with conn.cursor(pymysql.cursors.DictCursor) as cursor:
            
            # -------------------
            # Fetch artwork data
            # -------------------
            cursor.execute("""
                SELECT a.*, u.username, u.first_name, u.last_name, c.name AS category_name
                FROM artworks a
                JOIN users u ON a.user_id = u.id
                JOIN categories c ON a.category_id = c.id
                WHERE a.id = %s
            """, (artwork_id,))
            artwork = cursor.fetchone()

            if not artwork:
                abort(404, description="Artwork not found")

            # --------------
            # Fetch tags
            # --------------
            cursor.execute("""
                SELECT t.name
                FROM tags t
                JOIN artwork_tags at ON t.id = at.tag_id
                WHERE at.artwork_id = %s
            """, (artwork_id,))
            tags = [row['name'] for row in cursor.fetchall()]

            # ---------------------------------------------
            # If not logged in, show guest version directly
            # ---------------------------------------------
            if 'username' not in session:
                return render_template('artwork_guest_view.html', artwork=artwork, tags=tags)

            # ---------------------------
            # Fetch artwork reviews
            # ---------------------------
            cursor.execute("""
                SELECT r.*, u.first_name, u.last_name
                FROM reviews r
                JOIN users u ON r.buyer_id = u.id
                WHERE r.artwork_id = %s
                ORDER BY r.created_at DESC
            """, (artwork_id,))
            reviews = cursor.fetchall()

            # -------------------------------------
            # Get current user info (to pass along)
            # -------------------------------------
            cursor.execute("SELECT * FROM users WHERE username = %s", (session['username'],))
            user = cursor.fetchone()

            # --------------------------------------------------
            # Determine if this user is allowed to leave review
            # --------------------------------------------------
            can_review = False
            cursor.execute("""
                SELECT COUNT(*) AS count
                FROM orders o
                WHERE o.artwork_id = %s
                  AND o.buyer_username = %s
                  AND o.status = 'Sent to Delivery'
            """, (artwork_id, session['username']))
            result = cursor.fetchone()
            if result and result['count'] > 0:
                can_review = True

        # -----------------------
        # Render artwork detail
        # -----------------------
        return render_template(
            'artwork_detail.html',
            artwork=artwork,
            tags=tags,
            reviews=reviews,
            user=user,
            can_review=can_review
        )

    finally:
        conn.close()
        
@artwork_bp.route('/artwork/update_status/<int:artwork_id>', methods=['POST'])
def update_artwork_status(artwork_id):
    if 'username' not in session:
        return redirect(url_for('login_bp.login'))

    new_status = request.form.get('status')
    if not new_status:
        # If no status provided, redirect back without change
        return redirect(url_for('artwork_bp.artwork_detail', artwork_id=artwork_id))

    conn = get_db()
    try:
        with conn.cursor() as cursor:
            # Get current user id
            cursor.execute("SELECT id FROM users WHERE username = %s", (session['username'],))
            user = cursor.fetchone()
            if not user:
                return "User not found", 403

            # Verify ownership of artwork
            cursor.execute("SELECT id FROM artworks WHERE id = %s AND user_id = %s", (artwork_id, user['id']))
            artwork = cursor.fetchone()
            if not artwork:
                return "Unauthorized or artwork not found", 403

            # Update status
            cursor.execute("UPDATE artworks SET status = %s WHERE id = %s", (new_status, artwork_id))
        conn.commit()
    finally:
        conn.close()

    return redirect(url_for('artwork_bp.artwork_detail', artwork_id=artwork_id))
