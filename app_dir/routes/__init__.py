from flask import Flask


def register_routes(app: Flask) -> None:
    """Register all blueprint routes with the app_dir"""
    from app_dir.routes.accounts import accounts_bp
    from app_dir.routes.auth import auth_bp
    from app_dir.routes.transactions import transactions_bp
    from app_dir.routes.user import user_bp

    app.register_blueprint(auth_bp, url_prefix="/api/auth")
    app.register_blueprint(accounts_bp, url_prefix="/api/accounts")
    app.register_blueprint(transactions_bp, url_prefix="/api/transactions")
    app.register_blueprint(user_bp, url_prefix="/api/user")
