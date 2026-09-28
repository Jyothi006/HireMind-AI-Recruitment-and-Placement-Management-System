import os
from flask import Flask, render_template
from flask_login import LoginManager
from config import Config
from models import db
from models.user import User

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    # Ensure upload directory exists
    os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
    os.makedirs(os.path.join(Config.BASE_DIR, 'instance'), exist_ok=True)

    # Initialize extensions
    db.init_app(app)

    login_manager = LoginManager()
    login_manager.login_view = 'auth.login'
    login_manager.login_message_category = 'warning'
    login_manager.init_app(app)

    @login_manager.user_loader
    def load_user(user_id):
        return User.query.get(int(user_id))

    # Register Blueprints
    from routes.auth import auth_bp
    from routes.candidate import candidate_bp
    from routes.recruiter import recruiter_bp
    from routes.placement import placement_bp
    from routes.assessment import assessment_bp
    from routes.interview import interview_bp
    from routes.hiring import hiring_bp
    from routes.admin import admin_bp

    app.register_blueprint(auth_bp)
    app.register_blueprint(candidate_bp)
    app.register_blueprint(recruiter_bp)
    app.register_blueprint(placement_bp)
    app.register_blueprint(assessment_bp)
    app.register_blueprint(interview_bp)
    app.register_blueprint(hiring_bp)
    app.register_blueprint(admin_bp)

    @app.route('/')
    def index():
        return render_template('index.html')

    # Global Error Handlers
    @app.errorhandler(404)
    def page_not_found(e):
        return render_template('base.html', content="<div class='container py-5 text-center'><h2>404 - Page Not Found</h2><p>The requested page does not exist.</p><a href='/' class='btn btn-primary'>Return Home</a></div>"), 404

    @app.errorhandler(500)
    def internal_server_error(e):
        return render_template('base.html', content="<div class='container py-5 text-center'><h2>500 - System Error</h2><p>An unexpected server error occurred.</p><a href='/' class='btn btn-primary'>Return Home</a></div>"), 500

    return app

app = create_app()

if __name__ == '__main__':
    with app.app_context():
        db.create_all()

    import os
    app.run(
        host="0.0.0.0",
        port=int(os.environ.get("PORT", 5000))
    )
