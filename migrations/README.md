# Migrations

The schema is created with `flask --app run init-db` (SQLAlchemy `create_all`). Flask-Migrate
was deliberately left out to keep the stack to the assessed technologies. To add versioned
migrations later: `pip install Flask-Migrate`, then `flask db init` in this folder.
