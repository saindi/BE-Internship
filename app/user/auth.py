import time

import jwt
from config import global_settings
from user.schemas import TokenSchema


def sign_jwt(email: str, password: str) -> TokenSchema:
    payload = {
        "email": email,
        "password": password,
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
