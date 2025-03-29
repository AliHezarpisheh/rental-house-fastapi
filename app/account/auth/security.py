"""Module providing security(auth-related) essentials for the application."""

from fastapi.security import OAuth2PasswordBearer

oauth2_scheme = OAuth2PasswordBearer("token", description="Oauth2 password flow scheme")
