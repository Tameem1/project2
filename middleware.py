# middleware.py
from fastapi import Depends, HTTPException
from fastapi.security import OAuth2PasswordBearer
from services.auth_service import decode_jwt_token
from jwt import PyJWTError

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="auth/token")

def get_current_user(token: str = Depends(oauth2_scheme)):
    try:
        payload = decode_jwt_token(token)
        return payload
    except PyJWTError:
        raise HTTPException(status_code=401, detail="Invalid token")