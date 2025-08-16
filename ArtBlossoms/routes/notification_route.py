from flask import Blueprint, render_template, session, redirect, url_for, flash, request, jsonify
from db import get_db

notification_bp = Blueprint('notification_bp', __name__)


# Route: View all report notifications
@notification_bp.route('/notifications')
def view_notifications():
    if 'username' not in session:
        flash("Please log in to view notifications.", "error")
        return redirect(url_for('login'))

    username = session['username']
    db = get_db()
    with db.cursor() as cursor:
        cursor.execute("""
            SELECT id, message, is_read, created_at
            FROM report_notifications
            WHERE reporter_username = %s
            ORDER BY created_at DESC
        """, (username,))
        notifications = cursor.fetchall()

        # Also fetch user info for display
        cursor.execute("SELECT * FROM users WHERE username = %s", (username,))
        user = cursor.fetchone()

    return render_template('report_notifications.html', notifications=notifications, user=user)


# Route: Mark individual notification as read
@notification_bp.route('/notifications/mark_read', methods=['POST'])
def mark_notification_read():
    if 'username' not in session:
        flash("Please log in first.", "error")
        return redirect(url_for('login'))

    notification_id = request.form.get('notification_id')
    if not notification_id:
        flash("Invalid notification ID.", "error")
        return redirect(url_for('notification_bp.view_notifications'))

    username = session['username']
    db = get_db()
    with db.cursor() as cursor:
        cursor.execute("""
            UPDATE report_notifications
            SET is_read = 1
            WHERE id = %s AND reporter_username = %s
        """, (notification_id, username))
    db.commit()

    flash("Notification marked as read.", "success")
    return redirect(url_for('notification_bp.view_notifications'))


# Optional Route: Get unread count (for notification badge etc.)
@notification_bp.route('/notifications/unread_count')
def unread_count():
    if 'username' not in session:
        return jsonify(unread_count=0)

    username = session['username']
    db = get_db()
    with db.cursor() as cursor:
        cursor.execute("""
            SELECT COUNT(*) FROM report_notifications
            WHERE reporter_username = %s AND is_read = 0
        """, (username,))
        count = cursor.fetchone()[0]

    return jsonify(unread_count=count)
