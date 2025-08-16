from flask import Blueprint, render_template, session, redirect
from db import get_db
from datetime import datetime

dashboard_bp = Blueprint('dashboard_bp', __name__)

@dashboard_bp.route('/dashboard')
def dashboard():
    if 'username' not in session:
        return redirect('/login')

    username = session['username']
    conn = get_db()
    stats = {}
    categories = []
    top_selling = []
    popular_artists = []
    monthly_revenue = []
    recent_orders = []

    try:
        with conn.cursor() as cursor:
            # Get user info
            cursor.execute("SELECT * FROM users WHERE username=%s", (username,))
            user = cursor.fetchone()

            # ARTIST STATS
            if user['role'] in ['artist', 'both']:
                cursor.execute("SELECT * FROM artworks WHERE user_id=%s", (user['id'],))
                artworks = cursor.fetchall()
                stats['total_artworks'] = len(artworks)
                stats['sold_out'] = sum(1 for a in artworks if a.get('status') == 'Sold out')
                stats['available'] = sum(1 for a in artworks if a.get('status') != 'Sold out')

                # Revenue and order status
                cursor.execute("""
                    SELECT o.status, SUM(a.price) AS revenue
                    FROM orders o
                    JOIN artworks a ON o.artwork_id = a.id
                    WHERE a.user_id=%s
                    GROUP BY o.status
                """, (user['id'],))
                order_stats = cursor.fetchall()
                stats['total_revenue'] = sum(float(o['revenue'] or 0) for o in order_stats)
                stats['pending'] = sum(1 for o in order_stats if o['status'] == 'Pending')
                stats['processing'] = sum(1 for o in order_stats if o['status'] in ['Accepted', 'Processing'])
                stats['sent'] = sum(1 for o in order_stats if o['status'] == 'Sent to Delivery')
                stats['rejected'] = sum(1 for o in order_stats if o['status'] == 'Rejected')

            # BUYER STATS
            if user['role'] in ['buyer', 'both']:
                cursor.execute("""
                    SELECT * FROM orders WHERE buyer_username=%s ORDER BY created_at DESC LIMIT 10
                """, (username,))
                recent_orders = cursor.fetchall()

            # Categories count
            cursor.execute("""
                SELECT c.name, COUNT(a.id) AS count
                FROM categories c
                LEFT JOIN artworks a ON a.category_id = c.id
                GROUP BY c.id
            """)
            categories = cursor.fetchall()

            # Top selling artworks
            cursor.execute("""
                SELECT a.title, u.first_name AS artist_first, u.last_name AS artist_last,
                       COUNT(o.id) AS sold_count, SUM(a.price) AS total_earned
                FROM orders o
                JOIN artworks a ON o.artwork_id = a.id
                JOIN users u ON a.user_id = u.id
                GROUP BY a.id
                ORDER BY sold_count DESC
                LIMIT 5
            """)
            top_selling = cursor.fetchall()

            # Most popular artists
            cursor.execute("""
                SELECT u.first_name, u.last_name, COUNT(o.id) AS total_sold, SUM(a.price) AS total_revenue
                FROM orders o
                JOIN artworks a ON o.artwork_id = a.id
                JOIN users u ON a.user_id = u.id
                GROUP BY u.id
                ORDER BY total_sold DESC
                LIMIT 5
            """)
            popular_artists = cursor.fetchall()

            # Monthly revenue (for current year)
            current_year = datetime.now().year
            cursor.execute(f"""
                SELECT MONTH(o.created_at) AS month, SUM(a.price) AS total
                FROM orders o
                JOIN artworks a ON o.artwork_id = a.id
                WHERE YEAR(o.created_at)={current_year}
                GROUP BY month
                ORDER BY month ASC
            """)
            month_data = cursor.fetchall()
            # Fill all 12 months
            months = ["Jan","Feb","Mar","Apr","May","Jun","Jul","Aug","Sep","Oct","Nov","Dec"]
            month_totals = {i+1:0 for i in range(12)}
            for row in month_data:
                month_totals[row['month']] = float(row['total'] or 0)
            monthly_revenue = [{'name': months[i-1], 'total': month_totals[i]} for i in range(1,13)]

    finally:
        conn.close()

    return render_template(
        'dashboard.html',
        stats=stats,
        categories=categories,
        top_selling=top_selling,
        popular_artists=popular_artists,
        monthly_revenue=monthly_revenue,
        recent_orders=recent_orders
    )