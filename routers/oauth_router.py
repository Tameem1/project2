# routers/oauth_router.py
from fastapi import APIRouter, Request, HTTPException, Depends
from fastapi.responses import RedirectResponse
from authlib.integrations.starlette_client import OAuth, OAuthError
import os
from sqlalchemy.orm import Session
from db.session import get_db
# from services.auth_service import register_user_from_oauth, create_jwt_token
import logging

router = APIRouter()
oauth = OAuth()

# Register Google provider
oauth.register(
    name='google',
    client_id=os.getenv("GOOGLE_CLIENT_ID"),
    client_secret=os.getenv("GOOGLE_CLIENT_SECRET"),
    server_metadata_url='https://accounts.google.com/.well-known/openid-configuration',
    client_kwargs={'scope': 'openid email profile'},
)

# Register GitHub provider
oauth.register(
    name='github',
    client_id=os.getenv("GITHUB_CLIENT_ID"),
    client_secret=os.getenv("GITHUB_CLIENT_SECRET"),
    access_token_url='https://github.com/login/oauth/access_token',
    authorize_url='https://github.com/login/oauth/authorize',
    api_base_url='https://api.github.com/',
    client_kwargs={'scope': 'user:email'},
)

@router.get("/auth/oauth/{provider}")
async def oauth_login(provider: str, request: Request):
    if provider not in ['google', 'github']:
        raise HTTPException(status_code=400, detail="Unsupported provider")
    redirect_uri = request.url_for('oauth_callback', provider=provider)
    return await oauth.create_client(provider).authorize_redirect(request, redirect_uri)

@router.get("/auth/oauth/{provider}/callback")
async def oauth_callback(provider: str, request: Request, db: Session = Depends(get_db)):
    if provider not in ['google', 'github']:
        raise HTTPException(status_code=400, detail="Unsupported provider")
    client = oauth.create_client(provider)
    try:
        token = await client.authorize_access_token(request)
    except OAuthError as error:
        logging.error(f"OAuth error for {provider}: {error.error}")
        raise HTTPException(status_code=400, detail=f"OAuth error: {error.error}")
    
    # For Google, parse the ID token; for GitHub, fetch user info manually.
    if provider == "google":
        user_info = await client.parse_id_token(request, token)
    else:  # GitHub
        user_info = await client.get('user').json()
        # If email is not provided, get primary verified email:
        if not user_info.get("email"):
            emails = await client.get('user/emails').json()
            for email_obj in emails:
                if email_obj.get("primary") and email_obj.get("verified"):
                    user_info["email"] = email_obj.get("email")
                    break

    if not user_info or not user_info.get("email"):
        raise HTTPException(status_code=400, detail="Failed to obtain user info from provider")
    
    # Create (or retrieve) the user from your database.
    # user = register_user_from_oauth(user_info, db)
    jwt_token = create_jwt_token({
        "sub": user.username,
        "customer_id": str(user.customer_id),
        "user_id": str(user.id)
    })
    # Redirect to your frontend—here we attach the token as a query parameter.
    return RedirectResponse(url=f"http://localhost:3000?token={jwt_token}")