from datetime import datetime, timedelta, timezone
import logging
from jose import JWTError, jwt
from typing import Optional

from app.models.auth_models import Claims


logger = logging.getLogger("jwt_handler")
logging.basicConfig(level=logging.INFO)


class JWTHandler:
    def __init__(
        self,
        
        secret: str,
        algorithm: str,
        issuer: str,
        audience: str,
        expire_minutes: int,
        default_expire_days: int,
        remember_expire_days: int,
    ):
        
        self.secret_key = secret
        self.algorithm = algorithm
        self.issuer = issuer
        self.audience = audience
        self.expire_minutes = expire_minutes
        self.default_expire_days = default_expire_days
        self.remember_expire_days = remember_expire_days

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

    def _encode_token(self, claims: Claims) -> str:
        try:
            to_encode = {
                "sub": claims.sub,
                "exp": claims.exp,
                "iss": claims.iss,
                "aud": claims.aud,
                "type": claims.type,
            }

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

    def create_access_token(self, username: str) -> str:
        claims = self.generate_claims(username)
        return self._encode_token(claims)

    def verify_token(self, token: str, expected_type: str = "access") -> Optional[str]:
        try:
            if not token:
                logger.warning("Empty token provided")
                return None

            payload = jwt.decode(
                token,
                self.secret_key,
                algorithms=[self.algorithm],
                audience=self.audience,
                issuer=self.issuer,
            )

            token_type = payload.get("type")

            if token_type != expected_type:
                logger.warning(f"Token type mismatch. Expected {expected_type}, got {token_type}")
                return None

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

    def generate_claims(
        self, username: str, expires_delta: Optional[timedelta] = None, is_refresh: bool = False
    ) -> Claims:
        if expires_delta:
            expire = datetime.now(timezone.utc) + expires_delta
        else:
            expire = datetime.now(timezone.utc) + timedelta(minutes=self.expire_minutes)

        return Claims(
            sub=username,
            exp=int(expire.timestamp()),
            iss=self.issuer,
            aud=self.audience,
            type="refresh" if is_refresh else "access",
        )

    def create_refresh_token(self, username: str, is_remember: bool = False) -> str:
        if is_remember:
            expires_delta = timedelta(days=self.remember_expire_days)
        else:
            expires_delta = timedelta(days=self.default_expire_days)

        claims = self.generate_claims(username, expires_delta, is_refresh=True)

        return self._encode_token(claims)

    
