import datetime
import os

from dotenv import load_dotenv

load_dotenv("env/config.env")


class Config:
    """Base configuration."""

    DEBUG = False
    TESTING = False
    JWT_SECRET_KEY = os.getenv("JWT_SECRET_KEY")
    DATABASE_URI = os.getenv("DATABASE_URI")


class DevelopmentConfig(Config):
    """Development configuration."""

    JWT_REFRESH_TOKEN_EXPIRES = datetime.timedelta(days=1)
    JWT_ACCESS_TOKEN_EXPIRES = datetime.timedelta(minutes=15)
    DEBUG = True


class ProductionConfig(Config):
    """Production configuration."""

    pass
