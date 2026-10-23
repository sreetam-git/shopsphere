import os

import jwt
from dotenv import load_dotenv
from fastapi import Depends, HTTPException
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

load_dotenv()

JWT_SECRET_KEY = os.getenv("JWT_SECRET_KEY")
JWT_ALGORITHM = os.getenv("JWT_ALGORITHM", "HS256")

if not JWT_SECRET_KEY:
    raise RuntimeError("JWT_SECRET_KEY is missing from .env")

bearer_scheme = HTTPBearer(auto_error=False)

def get_current_token_payload(
        credentials: HTTPAuthorizationCredentials | None = Depends(bearer_scheme)
) -> dict:
    if credentials is None:
        raise HTTPException(
            status_code=401,
            detail="Authentication required.",
            headers={"WWW-Authenticate": "Bearer"},
        )

    try:
        payload = jwt.decode(
            credentials.credentials,
            JWT_SECRET_KEY,
            algorithms=[JWT_ALGORITHM],
            options={"require": ["sub", "exp"]}
        )

    except jwt.ExpiredSignatureError:
        raise HTTPException(
            status_code=401,
            detail="Access token has expired.",
            headers={"WWW-Authenticate": "Bearer"},
        )
    except jwt.InvalidTokenError:
        raise HTTPException(
            status_code=401,
            detail="Invalid access token.",
            headers={"WWW-Authenticate": "Bearer"},
        )

    return payload

ADMIN_USER_IDS = {
    user_id.strip() for user_id in os.getenv("ADMIN_USER_IDS", "").split(",") if user_id.strip()
}

def get_current_admin(current_user: dict = Depends(get_current_token_payload)):
    user_id = str(current_user.get("sub", ""))

    if not user_id or user_id not in ADMIN_USER_IDS:
        raise HTTPException(
            403,
            "Admin Access Required"
        )

    return current_user