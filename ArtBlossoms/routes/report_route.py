from flask import Blueprint, request, redirect, render_template, session, flash, url_for
from db import get_db

report_bp = Blueprint('report_bp', __name__)

# --------------------------
# 👤 Report a User
# --------------------------
@report_bp.route('/report_user', methods=['GET', 'POST'])
def report_user():
    if 'username' not in session:
        flash("Please log in to report a user.", "error")
        return redirect(url_for('login_bp.login'))

    reported_username = request.args.get('username')
    if not reported_username:
        return "Missing reported username.", 400

    if request.method == 'POST':
        reason = request.form.get('reason')
        description = request.form.get('description', '').strip()
        reporter = session['username']

        if not reason:
            flash("Please select a reason for reporting.", "error")
            return redirect(url_for('report_bp.report_user', username=reported_username))

        db = get_db()
        cursor = db.cursor()
        cursor.execute("""
            INSERT INTO user_reports (reporter_username, reported_username, reason, description)
            VALUES (%s, %s, %s, %s)
        """, (reporter, reported_username, reason, description))
        db.commit()
        cursor.close()

        flash("User report submitted successfully.", "success")
        return redirect(url_for('profile_bp.profile', username=reported_username))

    return render_template('report_user.html', reported_username=reported_username)

# --------------------------
# 🖼️ Report an Artwork
# --------------------------
@report_bp.route('/report_artwork/<int:artwork_id>', methods=['POST'])
def report_artwork(artwork_id):
    if 'username' not in session:
        flash("Please log in to report an artwork.", "error")
        return redirect(url_for('login_bp.login'))

    reason = request.form.get('reason')
    description = request.form.get('description', '').strip()
    reporter = session['username']

    if not reason:
        flash("Please select a reason.", "error")
        return redirect(url_for('artwork_bp.artwork_detail', artwork_id=artwork_id))

    db = get_db()
    cursor = db.cursor()
    cursor.execute("""
        INSERT INTO artwork_reports (reporter_username, artwork_id, reason, description)
        VALUES (%s, %s, %s, %s)
    """, (reporter, artwork_id, reason, description))
    db.commit()
    cursor.close()

    flash("Artwork reported successfully.", "success")
    return redirect(url_for('artwork_bp.artwork_detail', artwork_id=artwork_id))

# --------------------------
# 👀 View My Reports (User)
# --------------------------
@report_bp.route('/my_reports')
def my_reports():
    if 'username' not in session:
        flash("Please log in to view your reports.", "error")
        return redirect(url_for('login_bp.login'))

    db = get_db()
    cursor = db.cursor()
    cursor.execute("""
        SELECT * FROM user_reports
        WHERE reporter_username = %s
        ORDER BY created_at DESC
    """, (session['username'],))
    reports = cursor.fetchall()
    cursor.close()

    return render_template('my_reports.html', reports=reports)
