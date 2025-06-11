from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse
from starlette.requests import Request
from contextlib import asynccontextmanager

from application.api.texts import router as texts_router
from infra.database import init_db

@asynccontextmanager
async def lifespan(app: FastAPI):
    await init_db()
    yield

templates = Jinja2Templates(directory='application/templates')

app = FastAPI(
    debug=True,
    lifespan=lifespan
)

app.mount('/static', StaticFiles(directory='application/static'), name='static')

app.include_router(texts_router)

@app.get('/', response_class=HTMLResponse)
async def read_root(request: Request):
    return templates.TemplateResponse('index.html', {'request': request})