# tests/conftest.py
import pytest
import os

# Set dummy env vars so Settings() doesn't fail during import
os.environ.setdefault("ENV", "TEST")
os.environ.setdefault("LOG_LEVEL", "DEBUG")
os.environ.setdefault("SERVICE_NAME", "TestService")
os.environ.setdefault("MONGODB_URI", "mongodb://localhost:27017")
os.environ.setdefault("DATABASE_NAME", "testdb")
os.environ.setdefault("REVIEW_COLLECTION", "Reviews")
os.environ.setdefault("USER_COLLECTION", "Users")
os.environ.setdefault("USER_MEDIA_ENTRY_COLLECTION", "UserMediaEntries")
os.environ.setdefault("JWT_SECRET_KEY", "test_secret_supersecure_key")
os.environ.setdefault("JWT_ALGORITHM", "HS256")
os.environ.setdefault("JWT_ACCESS_TOKEN_EXPIRE_MINUTES", "30")
os.environ.setdefault("JWT_REFRESH_TOKEN_EXPIRE_DAYS_DEFAULT", "60")
os.environ.setdefault("JWT_ISSUER", "TESTISSUER")
os.environ.setdefault("JWT_AUDIENCE", "TESTAUDIENCE")
os.environ.setdefault("TMDB_API_KEY", "test_key")
os.environ.setdefault("TMDB_ACCESS_TOKEN", "test_token")
