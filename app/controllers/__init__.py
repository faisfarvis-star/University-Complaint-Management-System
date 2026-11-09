def register_blueprints(app):
    from .auth import bp as auth_bp
    from .main import bp as main_bp
    from .student import bp as student_bp
    from .admin import bp as admin_bp
    from .staff import bp as staff_bp
    for bp in (auth_bp, main_bp, student_bp, admin_bp, staff_bp):
        app.register_blueprint(bp)
