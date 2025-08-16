from flask import Blueprint, session, render_template

logout_bp = Blueprint('logout_bp', __name__)

@logout_bp.route('/logout')
def logout():
    session.clear()
    return render_template('logout.html')
