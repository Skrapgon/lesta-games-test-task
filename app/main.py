from fastapi import FastAPI
from contextlib import asynccontextmanager

from application.api.document import router as document_router
from application.api.collection import router as collection_router
from application.api.user import router as auth_router
from application.api.info import router as info_router
from infra.database import init_db

@asynccontextmanager
async def lifespan(app: FastAPI):
    await init_db()
    yield


app = FastAPI(
    debug=True,
    lifespan=lifespan
)
app.include_router(document_router)
app.include_router(collection_router)
app.include_router(auth_router)
app.include_router(info_router)