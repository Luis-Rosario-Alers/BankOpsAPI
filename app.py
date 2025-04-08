import os

from flask import Flask, jsonify
from flask_cors import CORS
from flask_jwt_extended import JWTManager

from app.constants.http_status import (
    HTTP_RESOURCE_NOT_FOUND,
    HTTP_SERVER_ERROR,
    HTTP_UNAUTHORIZED,
)
from app.extensions import init_extensions
from app.routes import register_routes


def create_app():
    """Application factory function"""
    app = Flask(__name__)

    jwt = JWTManager(app)

    # Enable CORS for the desktop application
    CORS(app, resources={r"/api/*": {"origins": "*"}})

    app_config = os.environ.get("FLASK_ENV", "development")
    if app_config == "production":
        app.config.from_object("config.ProductionConfig")
    else:
        app.config.from_object("config.DevelopmentConfig")
        app.config["DEBUG"] = True

    # Database connection
    db_uri = os.environ.get(
        "DATABASE_URI", "mysql+mysqlconnector://user:pass@localhost/bankops"
    )
    app.config["SQLALCHEMY_DATABASE_URI"] = db_uri
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

    # Initialize extensions
    init_extensions(app)

    # Register all routes
    register_routes(app)

    # JWT Error handlers
    @jwt.unauthorized_loader
    def unauthorized_callback(error):
        return jsonify({"error": "Missing authorization header"}), HTTP_UNAUTHORIZED

    @jwt.invalid_token_loader
    def invalid_token_callback(error):
        return jsonify({"error": "Invalid token"}), HTTP_UNAUTHORIZED

    # Error handlers
    @app.errorhandler(404)
    def not_found(error):
        return jsonify({"error": "Not found"}), HTTP_RESOURCE_NOT_FOUND

    @app.errorhandler(500)
    def server_error(error):
        return jsonify({"error": "Internal server error"}), HTTP_SERVER_ERROR

    return app


if __name__ == "__main__":
    app = create_app()
    app.run(host="127.0.0.1", port=5000)
