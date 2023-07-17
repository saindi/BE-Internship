# This file is responsible for signing , encoding , decoding and returning JWTS
import time
from typing import Dict

import jwt
from config import global_settings


def token_response(token: str):
    return {
        "access_token": token
    }


def sign_jwt(email: str, password: str) -> Dict[str, str]:
    payload = {
        "email": email,
        "password": password,
        "expires": time.time() + 60 * 60 * 24
    }
    token = jwt.encode(payload, global_settings.jwt_secret, algorithm=global_settings.jwt_algorithm)

    return token_response(token)


def decode_jwt(token: str) -> dict:
    try:
        decoded_token = jwt.decode(token, global_settings.jwt_secret, algorithms=global_settings.jwt_algorithm)
        return decoded_token if decoded_token["expires"] >= time.time() else None
    except jwt.exceptions.DecodeError as err:
        return None
