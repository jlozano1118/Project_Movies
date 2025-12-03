from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from utils.db import crear_db
from routers import usuario, peliculaSerie, valoracion, rutina

app = FastAPI(
    title="API de Gestión de Películas, Valoraciones y Rutinas",
    description="API para gestionar usuarios, películas/series, valoraciones y rutinas",
    version="1.0.0"
)

# Configurar archivos estáticos y templates
app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")


@app.get("/", response_class=HTMLResponse)
async def home(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})


@app.on_event("startup")
def startup():
    crear_db()


# Incluir todos los routers
app.include_router(usuario.router)
app.include_router(peliculaSerie.router)
app.include_router(valoracion.router)
app.include_router(rutina.router)