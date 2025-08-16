from flask import Blueprint, session, redirect, url_for, flash, render_template, request
from db import get_db

cart_route = Blueprint('cart_route', __name__)


@cart_route.route('/cart/add/<int:artwork_id>')
def add_to_cart(artwork_id):
    if 'username' not in session:
        return redirect(url_for('login'))

    username = session['username']
    conn = get_db()

    with conn.cursor() as cursor:
        # Prevent adding own artwork
        cursor.execute("""
            SELECT u.username 
            FROM artworks a
            JOIN users u ON a.user_id = u.id
            WHERE a.id = %s
        """, (artwork_id,))
        artist = cursor.fetchone()
        if artist and artist['username'] == username:
            flash("You cannot add your own artwork to the cart.")
            return redirect(url_for('artwork_bp.artwork_detail', artwork_id=artwork_id))

        # Prevent duplicate in cart
        cursor.execute("SELECT * FROM carts WHERE buyer_username = %s AND artwork_id = %s", (username, artwork_id))
        if cursor.fetchone():
            flash("This artwork is already in your cart.")
            return redirect(url_for('artwork_bp.artwork_detail', artwork_id=artwork_id))

        # Add to cart
        cursor.execute("INSERT INTO carts (buyer_username, artwork_id) VALUES (%s, %s)", (username, artwork_id))
        conn.commit()

    flash("Artwork added to cart successfully!")
    return redirect(url_for('artwork_bp.artwork_detail', artwork_id=artwork_id))


@cart_route.route('/my_cart')
def view_cart():
    if 'username' not in session:
        return redirect(url_for('login'))

    username = session['username']
    conn = get_db()

    with conn.cursor() as cursor:
        cursor.execute("""
            SELECT a.id, a.title, a.price, a.image, u.first_name, u.last_name, u.id AS artist_user_id
            FROM carts c
            JOIN artworks a ON c.artwork_id = a.id
            JOIN users u ON a.user_id = u.id
            WHERE c.buyer_username = %s
        """, (username,))
        items = cursor.fetchall()

    artists = {}
    grand_total = 0

    for item in items:
        artist_name = f"{item['first_name']} {item['last_name']}"
        if artist_name not in artists:
            artists[artist_name] = {'artworks': [], 'subtotal': 0, 'delivery': 200}
        artists[artist_name]['artworks'].append(item)
        artists[artist_name]['subtotal'] += float(item['price'])

    for artist_data in artists.values():
        artist_data['total'] = artist_data['subtotal'] + artist_data['delivery']
        grand_total += artist_data['total']

    return render_template('my_cart.html', artists=artists, grand_total=grand_total)


@cart_route.route('/cart/delete/<int:artwork_id>', methods=['POST'])
def delete_from_cart(artwork_id):
    if 'username' not in session:
        return redirect(url_for('login'))

    username = session['username']
    conn = get_db()

    with conn.cursor() as cursor:
        cursor.execute("DELETE FROM carts WHERE buyer_username = %s AND artwork_id = %s", (username, artwork_id))
        conn.commit()

    flash("Artwork removed from cart.")
    return redirect(url_for('cart_route.view_cart'))


@cart_route.route('/place_cart_order', methods=['GET', 'POST'])
def place_cart_order():
    if 'username' not in session:
        return redirect(url_for('login'))

    username = session['username']
    conn = get_db()
    cart_items = []
    total_price = 0.0
    artist_user_ids = set()

    with conn.cursor() as cursor:
        # Get all cart items
        cursor.execute("""
            SELECT a.id, a.title, a.price, a.image, u.first_name, u.last_name, u.id AS artist_user_id
            FROM carts c
            JOIN artworks a ON c.artwork_id = a.id
            JOIN users u ON a.user_id = u.id
            WHERE c.buyer_username = %s
        """, (username,))
        cart_items = cursor.fetchall()

        if not cart_items:
            flash("Your cart is empty!")
            return redirect(url_for('cart_route.view_cart'))

        for item in cart_items:
            total_price += float(item['price'])
            artist_user_ids.add(item['artist_user_id'])

        delivery_charge = 60 * len(artist_user_ids)
        grand_total = total_price + delivery_charge

        cursor.execute("SELECT id, name FROM districts ORDER BY name")
        districts = cursor.fetchall()

    if request.method == 'POST':
        buyer_name = request.form.get('buyer_name', '').strip()
        mobile = request.form.get('mobile', '').strip()
        email = request.form.get('email', '').strip()
        address = request.form.get('address', '').strip()
        district_id = request.form.get('district_id')
        postcode = request.form.get('postcode', '').strip() or None
        message = request.form.get('message', '').strip() or None

        if not all([buyer_name, mobile, email, address, district_id]):
            flash("Please fill in all required fields.")
            return redirect(url_for('cart_route.place_cart_order'))

        with conn.cursor() as cursor:
            for item in cart_items:
                cursor.execute("""
                    INSERT INTO orders (
                        artwork_id, buyer_username, buyer_name, mobile, email,
                        address, district_id, postcode, message, total_price
                    ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                """, (
                    item['id'], username, buyer_name, mobile, email,
                    address, district_id, postcode, message, item['price']
                ))
                order_id = cursor.lastrowid

                cursor.execute("""
                    INSERT INTO order_notifications (artist_id, order_id, is_read, created_at)
                    VALUES (%s, %s, FALSE, NOW())
                """, (item['artist_user_id'], order_id))

            # Clear cart
            cursor.execute("DELETE FROM carts WHERE buyer_username = %s", (username,))
            conn.commit()

        flash("Your order has been placed successfully!")
        return redirect(url_for('cart_route.view_cart'))

    return render_template(
        'place_cart_order.html',
        cart_items=cart_items,
        total_price=total_price,
        delivery_charge=delivery_charge,
        grand_total=grand_total,
        districts=districts
    )