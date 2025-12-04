from fastapi import FastAPI, UploadFile, File, Form, Request, HTTPException, Depends
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from sqlmodel import Session, select
from utils.db import crear_db, get_session
from data.models import Usuario, PeliculaSerie, Valoracion, Rutina
from routers import usuario, peliculaSerie, valoracion, rutina, web
import images

app = FastAPI(
    title="CineHub API",
    description="Sistema de Gestión de Películas",
    version="1.0.0"
)

app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")

@app.on_event("startup")
def startup():
    crear_db()

@app.get("/", response_class=HTMLResponse)
async def home(request: Request, session: Session = Depends(get_session)):
    n_usuarios = len(session.exec(select(Usuario).where(Usuario.is_active == True)).all())
    n_titulos = len(session.exec(select(PeliculaSerie).where(PeliculaSerie.is_active == True)).all())
    n_valoraciones = len(session.exec(select(Valoracion).where(Valoracion.is_active == True)).all())
    n_rutinas = len(session.exec(select(Rutina).where(Rutina.is_active == True)).all())

    return templates.TemplateResponse("index.html", {
        "request": request,
        "n_usuarios": n_usuarios,
        "n_titulos": n_titulos,
        "n_valoraciones": n_valoraciones,
        "n_rutinas": n_rutinas
    })

app.include_router(web.router)
app.include_router(usuario.router)
app.include_router(peliculaSerie.router)
app.include_router(valoracion.router)
app.include_router(rutina.router)
