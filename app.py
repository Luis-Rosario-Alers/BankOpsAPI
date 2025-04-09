import os

from flask import Blueprint, Flask, jsonify
from flask_cors import CORS

from app_dir.constants.http_status import (
    HTTP_RESOURCE_NOT_FOUND,
    HTTP_SERVER_ERROR,
)
from app_dir.extensions import init_extensions
from app_dir.routes.accounts import accounts_bp
from app_dir.routes.auth import auth_bp
from app_dir.routes.transactions import transactions_bp
from app_dir.routes.user import user_bp

app = Flask(__name__)

# Enable CORS for the desktop application
CORS(app, resources={r"/api/*": {"origins": "*"}})

app_config = os.environ.get("FLASK_ENV", "development")
if app_config == "production":
    app.config.from_object("config.config.ProductionConfig")
else:
    app.config.from_object("config.config.DevelopmentConfig")
    app.config["DEBUG"] = True

# Database connection
db_uri = os.environ.get(
    "DATABASE_URI", "mysql+mysqlconnector://user:pass@localhost/bankops"
)
app.config["SQLALCHEMY_DATABASE_URI"] = db_uri
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

# Initialize extensions
init_extensions(app)

# These blueprints are set up like this because it allows me to be able to use
# pycharm HTTP client to test the endpoints.
bp = Blueprint("api", __name__, url_prefix="/api")
bp.register_blueprint(auth_bp, url_prefix="/auth")
bp.register_blueprint(accounts_bp, url_prefix="/accounts")
bp.register_blueprint(transactions_bp, url_prefix="/transactions")
bp.register_blueprint(user_bp, url_prefix="/user")
app.register_blueprint(bp)


# Error handlers
@app.errorhandler(404)
def not_found(error):
    return jsonify({"error": "Not found"}), HTTP_RESOURCE_NOT_FOUND


@app.errorhandler(500)
def server_error(error):
    return jsonify({"error": "Internal server error"}), HTTP_SERVER_ERROR


app.run(host="127.0.0.1", port=5000)
