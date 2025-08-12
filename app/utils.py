
from passlib.context import CryptContext
from sqlalchemy.ext.asyncio import AsyncSession
from app.Models.user import User
from sqlalchemy.future import select
from fastapi import HTTPException,status,Request
from fastapi.security import OAuth2PasswordBearer
from datetime import datetime, timedelta, timezone
from app.settings import Settings
import jwt
from app.Models.user import UserRole

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")
setting = Settings()


pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def hash_password(password: str) -> str:
        return pwd_context.hash(password)

def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)

async def authenticate(db: AsyncSession, email: str, password: str):
    result = await db.execute(select(User).where(User.email == email))
    user = result.scalars().first()
    if not user or not verify_password(password, user.passwords):
        return None
    return user

def create_access_token(data: dict, expires_delta: timedelta | None = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.now(timezone.utc) + expires_delta
    else:
        expire = datetime.now(timezone.utc) + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, setting.SECRET_KEY, algorithm=setting.ALGORITHM)
    return encoded_jwt

async def get_current_user(token: str, db: AsyncSession):

        payload = jwt.decode(token, setting.SECRET_KEY, algorithms=[setting.ALGORITHM])
        email: str = payload.get("email")

        if email is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid token payload",
            )

        result = await db.execute(select(User).where(User.email == email))
        user = result.scalars().first()

        if user is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail=f"User Not Found"
            )
        return user

def require_role(self, role: UserRole):
        async def checker(request: Request):
            user = request.state.user
            if not user or user.role != role:
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail="Access forbidden: Insufficient role",
                )
            return user

        return checker




    
    

    