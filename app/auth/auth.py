import time
import jwt

from fastapi import Request, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from config import global_settings
from auth.schemas import TokenSchema
from db.database import async_session
from user.models import UserModel
from utils.hashing import Hasher


class JWTBearer(HTTPBearer):
    def __init__(self):
        super(JWTBearer, self).__init__()

    async def __call__(self, request: Request):
        credentials: HTTPAuthorizationCredentials = await super(JWTBearer, self).__call__(request)
        if credentials:
            if not credentials.scheme == "Bearer":
                raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Invalid authentication scheme.")

            user = await self.verify(credentials.credentials)

            if not user:
                raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Invalid token or expired token.")

            return user
        else:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Invalid authorization code.")

    async def verify(self, token: str) -> UserModel or None:
        result_jwt = await self.verify_jwt(token)

        if result_jwt:
            return result_jwt

        result_auth0 = await self.verify_auth0(token)

        if result_auth0:
            return result_auth0

        return None

    async def verify_jwt(self, token: str) -> UserModel or None:
        payload = self.decode_jwt(token)

        if not payload:
            return None

        async with async_session() as db:
            user = await UserModel.get_by_fields(db, email=payload['email'])

        if not user:
            return None

        return user

    async def verify_auth0(self, token: str) -> UserModel or None:
        payload = self.decode_auth0(token)

        if not payload:
            return None

        async with async_session() as db:
            user = await UserModel.get_by_fields(db, email=payload['email'])

            if user:
                return user

            new_user = UserModel(
                email=payload['email'],
                username=payload['email'],
                hashed_password=Hasher.get_password_hash(payload['email'])
            )

            await new_user.create(db)

        return new_user

    @staticmethod
    def sign_jwt(email: str) -> TokenSchema:
        payload = {
            "email": email,
            "expires": time.time() + 60 * 60 * 24
        }

        token = jwt.encode(payload, global_settings.jwt_secret, algorithm=global_settings.jwt_algorithm)

        return TokenSchema(access_token=token)

    @staticmethod
    def decode_jwt(token: str) -> dict or None:
        try:
            decoded_token = jwt.decode(token, global_settings.jwt_secret, algorithms=global_settings.jwt_algorithm)
            return decoded_token if decoded_token["expires"] >= time.time() else None

        except jwt.exceptions.DecodeError as err:
            return None

        except jwt.exceptions.InvalidAlgorithmError as err:
            return None

    @staticmethod
    def decode_auth0(token: str) -> dict or None:
        try:
            jwks_url = f'https://{global_settings.auth0_domain}/.well-known/jwks.json'
            jwks_client = jwt.PyJWKClient(jwks_url)

            signing_key = jwks_client.get_signing_key_from_jwt(token).key

            decoded_token = jwt.decode(
                token,
                signing_key,
                algorithms=global_settings.auth0_algorithms,
                audience=global_settings.auth0_api_audience,
                issuer=global_settings.auth0_issuer,
            )

            return decoded_token if decoded_token["exp"] >= time.time() else None

        except:
            return None


jwt_bearer = JWTBearer()