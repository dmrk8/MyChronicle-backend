import secrets
from datetime import datetime, timedelta, timezone
from typing import Optional
import structlog
from redis.asyncio import Redis
from app.models.auth_models import SessionData

logger = structlog.get_logger("session_handler")


class SessionHandler:
    """Handles server-side sessions that map to refresh tokens"""

    def __init__(self, redis_client: Redis, session_expire_days: int):
        self.redis_client = redis_client
        self.session_expire_days = session_expire_days

    def generate_session_id(self) -> str:
        """Generate a cryptographically secure session ID"""
        return secrets.token_urlsafe(32)

    async def create_session(self, user_id: str, refresh_token: str) -> str:
        """
        Create a new session and store the refresh token server-side

        Returns:
            session_id: To be sent to client as HTTP-only cookie
        """
        session_id = self.generate_session_id()

        session_data = SessionData(
            userId=user_id,
            refreshToken=refresh_token,
        )

        ttl = self.session_expire_days * 86400

        await self.redis_client.hset(
            f"session:{session_id}", mapping=session_data.model_dump(mode="json")
        )

        await self.redis_client.expire(f"session:{session_id}", ttl)

        # Also maintain a user->session mapping for logout
        await self.redis_client.set(f"user_session:{user_id}", session_id, ex=ttl)

        logger.info("Session created", session_id=session_id[:8], user_id=user_id)
        return session_id

    async def get_session(self, session_id: str) -> Optional[SessionData]:
        """Retrieve session data including refresh token"""
        try:
            data = await self.redis_client.hgetall(f"session:{session_id}")

            if not data:
                return None

            # Redis returns bytes, decode them
            decoded_data = {
                k.decode() if isinstance(k, bytes) else k: (
                    v.decode() if isinstance(v, bytes) else v
                )
                for k, v in data.items()
            }

            # Parse into SessionData model
            return SessionData.model_validate(decoded_data)
        except Exception as e:
            logger.error("Error retrieving session", error=str(e))
            return None

    async def delete_session(self, session_id: str):
        """Delete a session"""
        session_data = await self.get_session(session_id)

        if session_data:
            user_id = session_data.user_id 
            await self.redis_client.delete(f"session:{session_id}")

            if user_id:
                await self.redis_client.delete(f"user_session:{user_id}")

            logger.info("Session deleted", session_id=session_id[:8])

    async def delete_user_sessions(self, user_id: str):
        """Delete all sessions for a user (useful for logout)"""
        session_id = await self.redis_client.get(f"user_session:{user_id}")

        if session_id:
            if isinstance(session_id, bytes):
                session_id = session_id.decode()
            await self.delete_session(session_id)

        logger.info("User sessions deleted", user_id=user_id)
