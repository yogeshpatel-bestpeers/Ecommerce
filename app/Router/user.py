from fastapi import APIRouter,Depends,Response,status,HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from app.database import get_db
from app.Schema.user import User_Created,User_Login
from app.Models.user import User
from fastapi_utils.cbv import cbv
from app.utils import hash_password,create_access_token,authenticate
from datetime import timedelta
from app.settings import setting

router  = APIRouter()




@cbv(router)
class User_Auth:
    db: AsyncSession = Depends(get_db)

    @router.post("/signup")
    async def signup(self, request: User_Created):
    
        user_data = request.model_dump()
        user_data['passwords'] = hash_password(request.passwords)

        user = User(**user_data)

  
        self.db.add(user)
        await self.db.commit()
        await self.db.refresh(user)

        return {"detail": "Created Successfully"}
    
    @router.post("/login")
    async def login(self,request : User_Login):
        
        user = await authenticate(
            self.db, request.email, request.passwords
        )
        if not user :
            raise HTTPException(
                            status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid credentials"
                        )
        access_token_expires = timedelta(minutes=setting.ACCESS_TOKEN_EXPIRE_MINUTES)

        access_token = create_access_token(
            data={"sub": user.email}, expires_delta=access_token_expires
        )
        
        return {'type':'Bearear_token','acess_token' : access_token}
