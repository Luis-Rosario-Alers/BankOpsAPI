import os

from dotenv import load_dotenv

load_dotenv("env/config.env")


class Config:
    """Base configuration."""

    DEBUG = False
    TESTING = False
    SECRET_KEY = os.getenv("SECRET_KEY")
    DATABASE_URI = os.getenv("DATABASE_URI")


class DevelopmentConfig(Config):
    """Development configuration."""

    DEBUG = True


class ProductionConfig(Config):
    """Production configuration."""

    SECRET_KEY = os.getenv("SECRET_KEY")
    DATABASE_URI = os.getenv("DATABASE_URI")
