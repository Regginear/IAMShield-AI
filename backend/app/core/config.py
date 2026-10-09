import os
from datetime import timedelta

# Database Configuration
# SQLite keeps the research prototype runnable for demonstrations; production can
# override this with MySQL or PostgreSQL through DATABASE_URL.
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./iamshield.db")
SQLALCHEMY_ECHO = os.getenv("SQLALCHEMY_ECHO", "False") == "True"

# JWT Configuration
SECRET_KEY = os.getenv("SECRET_KEY", "your-secret-key-change-in-production")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "30"))
REFRESH_TOKEN_EXPIRE_DAYS = int(os.getenv("REFRESH_TOKEN_EXPIRE_DAYS", "7"))

# Application Configuration
APP_NAME = "IAMShield AI"
APP_VERSION = "1.0.0"
DEBUG = os.getenv("DEBUG", "False") == "True"

# CORS Configuration
ALLOWED_ORIGINS = os.getenv("ALLOWED_ORIGINS", "http://localhost:5173,http://localhost:3000").split(",")

# Logging Configuration
LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")
