from flask import Blueprint, render_template, redirect, session

home_bp = Blueprint('home_bp', __name__)

@home_bp.route('/')
def home():
    return render_template('home.html')

@home_bp.route('/guest')
def guest():
    if 'username' in session:
        return redirect('/profile')
    return redirect('/browse_artworks')