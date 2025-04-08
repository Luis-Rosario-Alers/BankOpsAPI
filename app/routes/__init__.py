from app.routes.accounts import accounts_bp
from app.routes.auth import auth_bp
from app.routes.transactions import transactions_bp


def register_routes(app):
    """Register all blueprint routes with the app"""
    app.register_blueprint(auth_bp, url_prefix="/api/auth")
    app.register_blueprint(accounts_bp, url_prefix="/api/accounts")
    app.register_blueprint(transactions_bp, url_prefix="/api/transactions")
