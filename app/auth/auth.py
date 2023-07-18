import time
import jwt

from fastapi import Request, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials

from config import global_settings
from auth.schemas import TokenSchema


def sign_jwt(email: str) -> TokenSchema:
    payload = {
        "email": email,
        "expires": time.time() + 60 * 60 * 24
    }
    token = jwt.encode(payload, global_settings.jwt_secret, algorithm=global_settings.jwt_algorithm)

    return TokenSchema(access_token=token)


def decode_jwt(token: str) -> dict:
    try:
        decoded_token = jwt.decode(token, global_settings.jwt_secret, algorithms=global_settings.jwt_algorithm)
        return decoded_token if decoded_token["expires"] >= time.time() else None
    except jwt.exceptions.DecodeError as err:
        return None


class JWTBearer(HTTPBearer):
    def __init__(self):
        super(JWTBearer, self).__init__()

    async def __call__(self, request: Request):
        credentials: HTTPAuthorizationCredentials = await super(JWTBearer, self).__call__(request)
        if credentials:
            if not credentials.scheme == "Bearer":
                raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Invalid authentication scheme.")
            if not self.verify_jwt(credentials.credentials):
                raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Invalid token or expired token.")
            return decode_jwt(credentials.credentials)
        else:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Invalid authorization code.")

    def verify_jwt(self, token: str) -> bool:
        try:
            payload = decode_jwt(token)
        except:
            payload = None

        return True if payload else False
