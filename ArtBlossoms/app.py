from flask import Flask, session, redirect, render_template
from routes.home_route import home_bp
from routes.register_route import register_bp
from routes.login_route import login_bp
from routes.profile_route import profile_bp
from routes.logout_route import logout_bp
from routes.artwork_route import artwork_bp
from routes.browse_artworks_route import browse_bp
from routes.cart_route import cart_route 
from routes.order_route import order_bp
from routes.upload_artwork_route import upload_bp
from routes.review_route import review_bp
from routes.report_route import report_bp
from routes.admin_report_route import admin_bp
from routes.custom_request_route import custom_bp
from routes.dashboard_route import dashboard_bp

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = 'static/uploads'
app.secret_key = 'something_secret'

# Register blueprints
app.register_blueprint(home_bp)
app.register_blueprint(register_bp)
app.register_blueprint(login_bp)
app.register_blueprint(profile_bp)
app.register_blueprint(logout_bp)
app.register_blueprint(artwork_bp)
app.register_blueprint(browse_bp)
app.register_blueprint(cart_route)
app.register_blueprint(order_bp)
app.register_blueprint(upload_bp)
app.register_blueprint(review_bp)
app.register_blueprint(report_bp)
app.register_blueprint(admin_bp)
app.register_blueprint(custom_bp)
app.register_blueprint(dashboard_bp)
@app.route('/')
def home():
    return render_template('home.html')



@app.route('/logout')
def logout():
    session.clear()
    return render_template('logout.html')

if __name__ == '__main__':
    app.run(debug=True)
