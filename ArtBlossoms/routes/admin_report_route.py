from flask import Blueprint, render_template, request, redirect, url_for, flash, session
from db import get_db

admin_bp = Blueprint('admin_bp', __name__)

# 🔐 Admin credentials (consider hashing in production)
ADMIN_USERNAME = 'superadmin'
ADMIN_PASSWORD = 'supersecret'

# ✅ Check if admin is logged in
def is_admin_logged_in():
    return session.get('is_admin') is True

# 🔒 Restrict all admin routes (except login)
@admin_bp.before_request
def restrict_admin_routes():
    allowed_endpoints = ['admin_bp.admin_login', 'static']
    if request.endpoint not in allowed_endpoints and not is_admin_logged_in():
        flash("Admin access required.", "error")
        return redirect(url_for('admin_bp.admin_login'))

# 🔐 Admin Login
@admin_bp.route('/admin/login', methods=['GET', 'POST'])
def admin_login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        if username == ADMIN_USERNAME and password == ADMIN_PASSWORD:
            session['is_admin'] = True
            flash("Logged in as admin.", "success")
            return redirect(url_for('admin_bp.admin_dashboard'))
        else:
            flash("Invalid admin credentials.", "error")
    return render_template('admin_login.html')

# 🚪 Admin Logout
@admin_bp.route('/admin/logout')
def admin_logout():
    session.pop('is_admin', None)
    flash("Admin logged out.", "success")
    return redirect(url_for('admin_bp.admin_login'))

# 🧭 Admin Dashboard
@admin_bp.route('/admin/dashboard')
def admin_dashboard():
    return render_template('admin_dashboard.html')

# =============================
# 📂 USER REPORT MANAGEMENT
# =============================

@admin_bp.route('/admin/user_reports')
def view_user_reports():
    db = get_db()
    cursor = db.cursor()
    cursor.execute("SELECT * FROM user_reports ORDER BY created_at DESC")
    reports = cursor.fetchall()
    cursor.close()
    return render_template('admin_user_reports.html', reports=reports)

@admin_bp.route('/admin/user_reports/dismiss', methods=['POST'])
def dismiss_user_report():
    report_id = request.form.get('report_id')
    if not report_id:
        flash("Invalid report ID.", "error")
        return redirect(url_for('admin_bp.view_user_reports'))

    db = get_db()
    cursor = db.cursor()
    cursor.execute("DELETE FROM user_reports WHERE id = %s", (report_id,))
    db.commit()
    cursor.close()

    flash("User report dismissed successfully.", "success")
    return redirect(url_for('admin_bp.view_user_reports'))

@admin_bp.route('/admin/ban_user', methods=['POST'])
def ban_user():
    username = request.form.get('username')
    if not username:
        flash("Invalid username.", "error")
        return redirect(url_for('admin_bp.view_user_reports'))

    db = get_db()
    cursor = db.cursor()
    cursor.execute("UPDATE users SET banned = 1 WHERE username = %s", (username,))
    db.commit()
    cursor.close()

    flash(f"User '{username}' has been banned.", "success")
    return redirect(url_for('admin_bp.view_user_reports'))

@admin_bp.route('/admin/unban_user', methods=['POST'])
def unban_user():
    username = request.form.get('username')
    if not username:
        flash("Invalid username.", "error")
        return redirect(url_for('admin_bp.view_user_reports'))

    db = get_db()
    cursor = db.cursor()
    cursor.execute("UPDATE users SET banned = 0 WHERE username = %s", (username,))
    db.commit()
    cursor.close()

    flash(f"User '{username}' has been unbanned.", "success")
    return redirect(url_for('admin_bp.view_user_reports'))

# =============================
# 🎨 ARTWORK REPORT MANAGEMENT
# =============================

@admin_bp.route('/admin/artwork_reports')
def view_artwork_reports():
    db = get_db()
    cursor = db.cursor()
    cursor.execute("""
        SELECT ar.id, ar.reporter_username, ar.artwork_id, a.title AS artwork_title,
            ar.reason, ar.description, ar.created_at, u.username AS artist_username,
            u.banned AS is_banned
        FROM artwork_reports ar
        JOIN artworks a ON ar.artwork_id = a.id
        JOIN users u ON a.user_id = u.id
        ORDER BY ar.created_at DESC
    """)


    reports = cursor.fetchall()
    cursor.close()
    return render_template('admin_artwork_reports.html', reports=reports)

@admin_bp.route('/admin/artwork_reports/dismiss', methods=['POST'], endpoint='dismiss_artwork_report')
def dismiss_artwork_report():
    report_id = request.form.get('report_id')
    if not report_id:
        flash("Invalid report ID.", "error")
        return redirect(url_for('admin_bp.view_artwork_reports'))

    db = get_db()
    cursor = db.cursor()
    cursor.execute("DELETE FROM artwork_reports WHERE id = %s", (report_id,))
    db.commit()
    cursor.close()

    flash("Artwork report dismissed successfully.", "success")
    return redirect(url_for('admin_bp.view_artwork_reports'))

@admin_bp.route('/admin/ban_artist', methods=['POST'])
def ban_artist():
    artist_username = request.form.get('artist_username')
    if not artist_username:
        flash("Invalid artist username.", "error")
        return redirect(url_for('admin_bp.view_artwork_reports'))

    db = get_db()
    cursor = db.cursor()
    cursor.execute("UPDATE users SET banned = 1 WHERE username = %s", (artist_username,))
    db.commit()
    cursor.close()

    flash(f"Artist '{artist_username}' has been banned.", "success")
    return redirect(url_for('admin_bp.view_artwork_reports'))

@admin_bp.route('/admin/unban_artist', methods=['POST'])
def unban_artist():
    artist_username = request.form.get('artist_username')
    if not artist_username:
        flash("Invalid artist username.", "error")
        return redirect(url_for('admin_bp.view_artwork_reports'))

    db = get_db()
    cursor = db.cursor()
    cursor.execute("UPDATE users SET banned = 0 WHERE username = %s", (artist_username,))
    db.commit()
    cursor.close()

    flash(f"Artist '{artist_username}' has been unbanned.", "success")
    return redirect(url_for('admin_bp.view_artwork_reports'))

@admin_bp.route('/admin/delete_artwork', methods=['POST'])
def delete_artwork():
    artwork_id = request.form.get('artwork_id')
    if not artwork_id:
        flash("Invalid artwork ID.", "error")
        return redirect(url_for('admin_bp.view_artwork_reports'))

    db = get_db()
    cursor = db.cursor()

    # Optional: Delete artwork reviews first (if ON DELETE CASCADE not set)
    cursor.execute("DELETE FROM reviews WHERE artwork_id = %s", (artwork_id,))
    
    # Optional: Delete artwork from carts
    cursor.execute("DELETE FROM carts WHERE artwork_id = %s", (artwork_id,))

    # Optional: Delete related tags
    cursor.execute("DELETE FROM artwork_tags WHERE artwork_id = %s", (artwork_id,))

    # Optional: Delete orders if artwork is still pending (optional)
    cursor.execute("DELETE FROM orders WHERE artwork_id = %s", (artwork_id,))

    # Finally: Delete the artwork
    cursor.execute("DELETE FROM artworks WHERE id = %s", (artwork_id,))
    db.commit()
    cursor.close()

    flash("Artwork has been deleted successfully.", "success")
    return redirect(url_for('admin_bp.view_artwork_reports'))




