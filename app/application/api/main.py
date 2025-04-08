from fastapi import FastAPI
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse
from starlette.requests import Request

from app.application.api.texts import router as texts_router

templates = Jinja2Templates(directory='app/application/templates')

app = FastAPI(
    debug=True
)

app.include_router(texts_router)

@app.get('/', response_class=HTMLResponse)
async def read_root(request: Request):
    return templates.TemplateResponse('index.html', {'request': request})