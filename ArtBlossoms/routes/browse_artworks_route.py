from flask import Blueprint, render_template, request, session
from db import get_db

browse_bp = Blueprint('browse_bp', __name__)

@browse_bp.route('/browse_artworks')
def browse_artworks():
    search_query = request.args.get('search', '').strip()
    category_filter = request.args.get('category', '').strip()
    sort_option = request.args.get('sort', 'newest')
    tag_filter = request.args.get('tag', '').strip()
    artist_query = request.args.get('artist', '').strip()

    conn = get_db()
    with conn.cursor() as cursor:
        # Fetch categories and tags for dropdowns
        cursor.execute("SELECT * FROM categories")
        categories = cursor.fetchall()

        cursor.execute("SELECT * FROM tags")
        tags = cursor.fetchall()

        # Build artwork query
        query = """
            SELECT
                a.id, a.title, a.image, a.price, a.upload_time,
                u.username, u.first_name, u.last_name,
                c.name AS category_name,
                COALESCE(AVG(r.rating), 0) AS avg_rating
            FROM artworks a
            JOIN users u ON a.user_id = u.id
            JOIN categories c ON a.category_id = c.id
            LEFT JOIN reviews r ON r.artwork_id = a.id
            LEFT JOIN artwork_tags at ON a.id = at.artwork_id
            LEFT JOIN tags t ON at.tag_id = t.id
            WHERE 1 = 1
        """
        params = []

        if search_query:
            query += " AND a.title LIKE %s"
            params.append(f"%{search_query}%")

        if artist_query:
            query += " AND (u.first_name LIKE %s OR u.last_name LIKE %s)"
            params.extend([f"%{artist_query}%", f"%{artist_query}%"])

        if category_filter:
            query += " AND c.id = %s"
            params.append(category_filter)

        if tag_filter:
            query += " AND t.id = %s"
            params.append(tag_filter)

        query += " GROUP BY a.id"

        sort_map = {
            'price_asc': 'a.price ASC',
            'price_desc': 'a.price DESC',
            'title_asc': 'a.title ASC',
            'title_desc': 'a.title DESC',
            'rating_desc': 'avg_rating DESC',
            'newest': 'a.upload_time DESC'
        }
        query += f" ORDER BY {sort_map.get(sort_option, 'a.upload_time DESC')}"

        cursor.execute(query, params)
        artworks = cursor.fetchall()

    conn.close()

    return render_template(
        'browse_artworks.html',
        artworks=artworks,
        categories=categories,
        tags=tags,
        search_query=search_query,
        selected_category=category_filter,
        selected_sort=sort_option,
        selected_tag=tag_filter,
        artist_query=artist_query
    )
