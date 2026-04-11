"""Authentication dependencies: JWT decoding, current user, role guard."""

import logging
import uuid

from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.config import get_settings
from app.db.session import get_db
from app.models.user import User

logger = logging.getLogger(__name__)
settings = get_settings()

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/auth/login")


async def get_current_user(
    token: str = Depends(oauth2_scheme),
    db: AsyncSession = Depends(get_db),
) -> User:
    """Decode JWT, load and return the User row. Raises 401 on failure."""
    credentials_exc = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Invalid or expired token",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=["HS256"])
        user_id_str: str | None = payload.get("sub")
        if user_id_str is None:
            logger.warning("JWT missing 'sub' claim")
            raise credentials_exc
        # Ensure token has an expiry claim
        if "exp" not in payload:
            logger.warning("JWT missing 'exp' claim")
            raise credentials_exc
        user_id = uuid.UUID(user_id_str)
    except (JWTError, ValueError) as e:
        logger.warning("JWT decode failed: %s", e)
        raise credentials_exc

    result = await db.execute(select(User).where(User.id == user_id))
    user = result.scalar_one_or_none()
    if user is None:
        logger.warning("JWT valid but user not found: %s", user_id)
        raise credentials_exc

    logger.debug("Authenticated user %s (%s)", user.email, user.role.value)
    return user


def require_role(*roles: str):
    """Return a dependency that checks the current user has one of the given roles."""

    async def _guard(current_user: User = Depends(get_current_user)) -> User:
        if current_user.role.value not in roles:
            logger.warning("Permission denied: user %s role=%s required=%s", current_user.email, current_user.role.value, roles)
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Insufficient permissions",
            )
        return current_user

    return _guard
