import time
import jwt

from fastapi import Request, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials

from config import global_settings
from auth.schemas import TokenSchema
from db.database import async_session
from user.models import UserModel


class JWTBearer(HTTPBearer):
    def __init__(self):
        super(JWTBearer, self).__init__()

    async def __call__(self, request: Request):
        credentials: HTTPAuthorizationCredentials = await super(JWTBearer, self).__call__(request)
        if credentials:
            if not credentials.scheme == "Bearer":
                raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Invalid authentication scheme.")

            user = await self.verify_jwt(credentials.credentials)

            if not user:
                raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Invalid token or expired token.")

            return user
        else:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Invalid authorization code.")

    async def verify_jwt(self, token: str) -> bool:
        try:
            async with async_session() as db:
                payload = self.decode_jwt(token)
                user = await UserModel.get_by_fields(db, email=payload['email'])
        except:
            user = None

        return user

    @staticmethod
    def sign_jwt(email: str) -> TokenSchema:
        payload = {
            "email": email,
            "expires": time.time() + 60 * 60 * 24
        }

        token = jwt.encode(payload, global_settings.jwt_secret, algorithm=global_settings.jwt_algorithm)

        return TokenSchema(access_token=token)

    @staticmethod
    def decode_jwt(token: str) -> dict:
        try:
            decoded_token = jwt.decode(token, global_settings.jwt_secret, algorithms=global_settings.jwt_algorithm)
            return decoded_token if decoded_token["expires"] >= time.time() else None
        except jwt.exceptions.DecodeError as err:
            return None
