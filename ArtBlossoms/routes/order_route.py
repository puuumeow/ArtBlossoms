from flask import Blueprint, render_template, request, redirect, session, url_for, flash
from db import get_db

order_bp = Blueprint('order_bp', __name__)

@order_bp.route('/order/<int:artwork_id>', methods=['GET', 'POST'])
def order_artwork(artwork_id):
    if 'username' not in session:
        return redirect(url_for('login'))

    conn = get_db()
    cursor = conn.cursor()

    # Fetch artwork details
    cursor.execute("SELECT id, title, price FROM artworks WHERE id = %s", (artwork_id,))
    artwork = cursor.fetchone()
    if not artwork:
        flash("Artwork not found.")
        return redirect(url_for('browse_artworks'))

    # Fetch district list
    cursor.execute("SELECT id, name FROM districts ORDER BY name ASC")
    districts = cursor.fetchall()

    if request.method == 'POST':
        buyer_username = session['username']
        buyer_name = request.form['buyer_name']
        mobile = request.form['mobile']
        email = request.form['email']
        address = request.form['address']
        district_id = request.form['district_id']
        postcode = request.form['postcode']
        message = request.form['message']
        total_price = artwork['price']

        # Fetch district name
        cursor.execute("SELECT name FROM districts WHERE id = %s", (district_id,))
        district_row = cursor.fetchone()
        district = district_row['name'] if district_row else ''

        # Insert into orders
        cursor.execute("""
            INSERT INTO orders (
                artwork_id, buyer_username, buyer_name, mobile, email, address,
                district, postcode, message, total_price, district_id
            ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        """, (
            artwork_id, buyer_username, buyer_name, mobile, email, address,
            district, postcode, message, total_price, district_id
        ))
        conn.commit()

        flash('Your order has been placed successfully! <a href="/browse_artworks">Browse more?</a>')

        # ✅ FIX: use the correct endpoint name for your cart
        return redirect(url_for('cart_route.view_cart'))

    return render_template('order_form.html', artwork=artwork, districts=districts)


@order_bp.route('/artist_orders')
def artist_orders():
    if 'user_id' not in session:
        return redirect(url_for('login_bp.login'))

    artist_id = session['user_id']
    conn = get_db()
    with conn.cursor() as cursor:
        cursor.execute("""
            SELECT o.*, a.title AS artwork_title, a.image AS artwork_image, u.username AS buyer_username
            FROM orders o
            JOIN artworks a ON o.artwork_id = a.id
            JOIN users u ON o.buyer_username = u.username
            WHERE a.user_id = %s
            ORDER BY o.created_at DESC
        """, (artist_id,))
        orders = cursor.fetchall()

        # Also fetch artist info
        cursor.execute("SELECT * FROM users WHERE id = %s", (artist_id,))
        user = cursor.fetchone()

    conn.close()
    return render_template('artist_orders.html', orders=orders, user=user)
