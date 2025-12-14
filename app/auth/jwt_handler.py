from datetime import datetime, timedelta, timezone
import logging
from jose import JWTError, jwt
from typing import Optional
from dotenv import load_dotenv
from app.models.auth_models import Claims

load_dotenv()

logger = logging.getLogger("jwt_handler")
logging.basicConfig(level=logging.INFO)


class JWTHandler:
    def __init__(self, secret: str, algorithm: str, issuer: str, audience: str, expire_minutes : int):
        self.secret_key = secret
        self.algorithm = algorithm
        self.issuer = issuer
        self.audience = audience
        self.expire_minutes = expire_minutes

        if not self.secret_key:
            raise ValueError("SECRET_KEY is required")
        if not self.algorithm:
            raise ValueError("ALGORITHM is required")
        if not self.issuer:
            raise ValueError("ISSUER is required")
        if not self.audience:
            raise ValueError("AUDIENCE is required")
        if not self.expire_minutes:
            raise ValueError("expire minutes is required")


    def create_access_token(self, claims: Claims) -> str:
        try:
            to_encode = {"sub": claims.sub, "exp": claims.exp, "iss": claims.iss, "aud": claims.aud}

            encoded_jwt = jwt.encode(to_encode, self.secret_key, algorithm=self.algorithm)  # type: ignore
            logger.info(f"Access token created for subject {claims.sub}")
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
    
    def generate_claims(self, username: str, expires_delta: Optional[timedelta] = None) -> Claims:
        if expires_delta:
            expire = datetime.now(timezone.utc) + expires_delta
        else:
            expire = datetime.now(timezone.utc) + timedelta(
                minutes=self.expire_minutes
            )

        return Claims(
            sub=username,
            exp=int(expire.timestamp()),
            iss=self.issuer,
            aud=self.audience,
        )       