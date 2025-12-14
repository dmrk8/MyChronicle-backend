import logging
from passlib.context import CryptContext

logger = logging.getLogger("__name__")
logging.basicConfig(level=logging.INFO)


class PasswordHandler:
    def __init__(self):
        self.pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

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
