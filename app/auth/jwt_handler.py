import logging
from jose import JWTError, jwt
from passlib.context import CryptContext
from datetime import datetime, timedelta
from typing import Optional
import os
from dotenv import load_dotenv

load_dotenv()

logger = logging.getLogger("jwt_handler")
logging.basicConfig(level=logging.INFO)


class JWTHandler:
    def __init__(self):
        self.pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
        self.secret_key = os.getenv("SECRET_KEY")
        self.algorithm = os.getenv("ALGORITHM")
        access_token_expire_str = os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES")
        self.issuer = os.getenv("ISSUER")
        self.audience = os.getenv("AUDIENCE")

        if not self.secret_key:
            raise ValueError("SECRET_KEY environment variable is not set")
        if not self.algorithm:
            raise ValueError("ALGORITHM environment variable is not set")
        if not access_token_expire_str:
            raise ValueError("ACCESS_TOKEN_EXPIRE_MINUTES environment variable is not set")
        try:
            self.access_token_expire_minutes = int(access_token_expire_str)
            if self.access_token_expire_minutes <= 0:
                raise ValueError("ACCESS_TOKEN_EXPIRE_MINUTES must be a positive integer")
        except ValueError:
            raise ValueError("ACCESS_TOKEN_EXPIRE_MINUTES must be a valid integer")
        if not self.issuer:
            raise ValueError("ISSUER environment variable is not set")
        if not self.audience:
            raise ValueError("AUDIENCE environment variable is not set")

    def create_access_token(self, sub: str, expires_delta: Optional[timedelta] = None) -> str:
        try:
            if expires_delta:
                expire = datetime.now() + expires_delta
            else:
                expire = datetime.now() + timedelta(minutes=self.access_token_expire_minutes)

            to_encode = {"sub": sub, "exp": expire, "iss": self.issuer, "aud": self.audience}

            encoded_jwt = jwt.encode(to_encode, self.secret_key, algorithm=self.algorithm)  # type: ignore
            logger.info(f"Access token created for subject {sub}")
            return encoded_jwt

        except ValueError as ve:
            logger.error(f"Validation error in create_access_token: {ve}")
            raise
        except JWTError as je:
            logger.error(f"JWT encoding error: {je}")
            raise
        except Exception as e:
            logger.error(f"Unexpected error in create_access_token: {e}")
            raise

    def verify_token(self, token: str) -> Optional[str]:
        try:
            if not token:
                logger.warning("Empty token provided")
                return None

            if self.secret_key is None:
                logger.error("SECRET_KEY is not configured")
                raise ValueError("SECRET_KEY is required for token verification")

            payload = jwt.decode(
                token,
                self.secret_key,
                algorithms=self.algorithm,
                audience=self.audience,
                issuer=self.issuer,
            )

            username = payload.get("sub")
            if username is None or not isinstance(username, str):
                logger.warning("Token missing subject or invalid type")
                return None

            logger.info(f"Token verified for user {username}")
            return username

        except JWTError as je:
            logger.warning(f"JWT verification failed: {je}")
            return None
        except Exception as e:
            logger.error(f"Unexpected error in verify_token: {e}")
            raise

    def hash_password(self, password: str) -> str:
        try:
            if not password:
                raise ValueError("Password cannot be empty")

            hashed = self.pwd_context.hash(password)
            logger.info("Password hashed successfully")
            return hashed

        except ValueError as ve:
            logger.error(f"Validation error in hash_password: {ve}")
            raise
        except Exception as e:
            logger.error(f"Unexpected error in hash_password: {e}")
            raise

    def verify_password(self, plain_password: str, hashed_password: str) -> bool:
        try:
            if not plain_password or not hashed_password:
                logger.warning("Empty password or hash provided")
                return False

            result = self.pwd_context.verify(plain_password, hashed_password)
            logger.info(f"Password verification: {result}")
            return result

        except Exception as e:
            logger.error(f"Unexpected error in verify_password: {e}")
            raise
