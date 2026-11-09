import os

from flask import Flask, render_template

from config import Config

from .extensions import csrf, db, login_manager


def create_app(config=None):
    app = Flask(__name__)
    app.config.from_object(config or Config)
    os.makedirs(app.instance_path, exist_ok=True)
    os.makedirs(app.config["UPLOAD_FOLDER"], exist_ok=True)

    db.init_app(app)
    csrf.init_app(app)
    login_manager.init_app(app)
    login_manager.login_view = "auth.login"
    login_manager.login_message_category = "warning"

    from . import models  # noqa: F401  (register tables)
    from .controllers import register_blueprints
    from .views import register_view_helpers
    from .repositories.implementations import SqlAlchemyUserRepository

    @login_manager.user_loader
    def load_user(user_id):
        user = SqlAlchemyUserRepository().get_by_id(int(user_id))
        return user if user and user.is_active else None

    register_blueprints(app)
    register_view_helpers(app)
    _register_errors(app)
    _register_cli(app)
    return app


def _register_errors(app):
    def make(code, title, text):
        def handler(_err):
            return render_template("errors/error.html", code=code, title=title, text=text), code
        return handler

    app.register_error_handler(403, make(403, "Access denied", "You do not have permission to view this page."))
    app.register_error_handler(404, make(404, "Page not found", "The page you requested does not exist."))
    app.register_error_handler(413, make(413, "File too large", "The upload exceeds the allowed size."))
    app.register_error_handler(500, make(500, "Something went wrong", "An unexpected error occurred. Please try again."))


def _register_cli(app):
    import click

    @app.cli.command("init-db")
    def init_db():
        """Create all database tables."""
        db.create_all()
        click.echo("Database initialised.")

    @app.cli.command("seed")
    @click.option("--reset", is_flag=True, help="Drop all tables first.")
    def seed(reset):
        """Load fictional development data."""
        from .utils.seed import seed_dev_data
        if reset:
            db.drop_all()
        db.create_all()
        click.echo(seed_dev_data())

    @app.cli.command("create-admin")
    @click.option("--email", prompt=True)
    @click.option("--name", prompt="Full name")
    @click.password_option()
    def create_admin(email, name, password):
        """Create an administrator account (admins cannot self-register)."""
        from .models import User
        from .repositories.implementations import SqlAlchemyUserRepository
        from .services.auth_service import _check_password_strength
        _check_password_strength(password)
        repo = SqlAlchemyUserRepository()
        if repo.get_by_email(email):
            raise click.ClickException("Email already exists.")
        user = User(full_name=name, email=email.lower(), role="admin")
        user.set_password(password)
        repo.create(user)
        click.echo(f"Admin {email} created.")
