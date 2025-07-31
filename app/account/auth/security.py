"""Module providing security(auth-related) essentials for the application."""

from fastapi.security import APIKeyHeader

api_key_scheme = APIKeyHeader(
    name="Authorization", description="Oauth2 password flow scheme"
)
