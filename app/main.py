from fastapi import FastAPI
from contextlib import asynccontextmanager
from app.database import engine,Base
from app.Router.user import router as auth
from app.Router.products import router as product
from app.middleware.middeware import AuthenticateMiddleware


@asynccontextmanager
async def lifspan(app : FastAPI):
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    try:
        yield
    finally:
        await engine.dispose()

app = FastAPI(lifespan=lifspan)
    
# app.add_middleware(AuthenticateMiddleware)
app.include_router(auth)
app.include_router(product)