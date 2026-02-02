# -*- coding: utf-8 -*-
from fastapi import FastAPI, Request
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse
from fastapi.middleware.cors import CORSMiddleware
from starlette.middleware.base import BaseHTTPMiddleware
import uvicorn
import json

from backend.database import init_db
from backend.routes import auth_routes, idp_routes, task_routes, logout_route, template_routes, comment_routes, user_routes

# Исправление JSON encoder для правильной кодировки кириллицы
from fastapi.encoders import jsonable_encoder as original_jsonable_encoder

def utf8_jsonable_encoder(obj, **kwargs):
    result = original_jsonable_encoder(obj, **kwargs)
    if isinstance(result, (dict, list)):
        return json.loads(json.dumps(result, ensure_ascii=False))
    return result

import fastapi.encoders
fastapi.encoders.jsonable_encoder = utf8_jsonable_encoder

# Middleware для установки charset=utf-8 в заголовках
class UTF8Middleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        response = await call_next(request)
        if response.headers.get("content-type"):
            content_type = response.headers["content-type"]
            if "application/json" in content_type and "charset" not in content_type:
                response.headers["content-type"] = "application/json; charset=utf-8"
            elif "text/html" in content_type and "charset" not in content_type:
                response.headers["content-type"] = "text/html; charset=utf-8"
            elif "text/plain" in content_type and "charset" not in content_type:
                response.headers["content-type"] = "text/plain; charset=utf-8"
        return response

app = FastAPI(
    title="ИПР - Индивидуальные планы развития",
    description="Веб-приложение для создания и управления ИПР сотрудников",
    version="1.0.0"
)

app.add_middleware(UTF8Middleware)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth_routes.router)
app.include_router(logout_route.router)
app.include_router(idp_routes.router)
app.include_router(task_routes.router)
app.include_router(template_routes.router)
app.include_router(comment_routes.router)
app.include_router(user_routes.router)

app.mount("/static", StaticFiles(directory="frontend/static"), name="static")
templates = Jinja2Templates(directory="frontend/templates")

@app.get("/", response_class=HTMLResponse)
async def index(request: Request):
    return templates.TemplateResponse("login.html", {"request": request})

@app.get("/dashboard", response_class=HTMLResponse)
async def dashboard(request: Request):
    return templates.TemplateResponse("dashboard.html", {"request": request})

@app.get("/profile", response_class=HTMLResponse)
async def profile(request: Request):
    return templates.TemplateResponse("profile.html", {"request": request})

@app.get("/kanban/{idp_id}", response_class=HTMLResponse)
async def kanban(request: Request, idp_id: int):
    return templates.TemplateResponse("kanban.html", {"request": request, "idp_id": idp_id})

@app.get("/create-idp", response_class=HTMLResponse)
async def create_idp_page(request: Request):
    return templates.TemplateResponse("create_idp.html", {"request": request})

@app.on_event("startup")
def on_startup():
    init_db()
    print("✅ База данных инициализирована")
    print("🚀 Приложение запущено: http://localhost:8000")
    print("📚 API документация: http://localhost:8000/docs")

if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)

