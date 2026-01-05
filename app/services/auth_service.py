import structlog
from app.models.auth_models import LoginRequest, AuthResponse
from app.auth.jwt_handler import JWTHandler
from app.services.user_service import UserService
from app.exceptions import AuthenticationError, TokenError


logger = structlog.get_logger("auth_service")

class AuthService:
    def __init__(self, jwt_handler: JWTHandler, user_service: UserService):
        self.jwt_handler = jwt_handler
        self.user_service = user_service

    async def login(self, user_login: LoginRequest) -> AuthResponse:
        try:
            user = await self.user_service.verify_credentials(
                user_login.username, user_login.password
            )

            if not user:
                raise AuthenticationError("Invalid username or password")

            logger.info("User logged in successfully", username=user.username)

            #access_token = self.jwt_handler.create_access_token(user.id)
            refresh_token = self.jwt_handler.create_refresh_token(user.id) 
            #await self.jwt_handler.store_refresh_token(user.id, refresh_token)
            # session_id = await self.session_handler.create_session(user.id, refresh_token)

            return AuthResponse(
                message="Login successful",
                accessToken=refresh_token,
               # session_id=session_id
            )

        except AuthenticationError as ae:
            logger.error("Login failed", error=str(ae), user_id=user_login.username)
            raise
        except Exception as e:
            logger.error(
                "Unexpected error during login", error=str(e), username=user_login.username
            )
            raise 
    
    #BELOW THIS NOT USED
    #NOT USED
    #NOT USED
    async def refresh_access_token(self, session_id: str) -> AuthResponse:
        """
    
        Client never sends refresh token directly
        """
        # Get session data (includes refresh token)
        session_data = await self.session_handler.get_session(session_id)

        if not session_data:
            raise TokenError("Invalid or expired session")

        user_id = session_data.user_id
        current_refresh_token = session_data.refresh_token

        if not user_id or not current_refresh_token:
            raise TokenError("Invalid session data")

        # Verify the refresh token
        verified_user_id = await self.jwt_handler.verify_refresh_token(
            current_refresh_token
        )

        if not verified_user_id or verified_user_id != user_id:
            # Session invalid, clean it up
            await self.session_handler.delete_session(session_id)
            raise TokenError("Invalid or expired refresh token")

        # Create new tokens
        new_access_token = self.jwt_handler.create_access_token(user_id)
        new_refresh_token = self.jwt_handler.create_refresh_token(user_id)

        # Revoke old refresh token and store new one
        await self.jwt_handler.revoke_refresh_token(user_id)
        await self.jwt_handler.store_refresh_token(user_id, new_refresh_token)

        # Update session with new refresh token
        await self.session_handler.delete_session(session_id)
        new_session_id = await self.session_handler.create_session(
            user_id, new_refresh_token
        )

        logger.info("Token refreshed", user_id=user_id)

        return AuthResponse(
            message="Token refreshed",
            accessToken=new_access_token,
            session_id=session_id,
        )

    async def logout(self, session_id: str):
        """Logout user by deleting session and revoking refresh token"""
        session_data = await self.session_handler.get_session(session_id)

        if session_data:
            user_id = session_data.user_id

            # Revoke refresh token
            if user_id:
                await self.jwt_handler.revoke_refresh_token(user_id)

            # Delete session
            await self.session_handler.delete_session(session_id)

            logger.info("User logged out", user_id=user_id)
