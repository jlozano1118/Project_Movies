from fastapi import FastAPI, UploadFile, File, Form, Request, HTTPException, Depends
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from sqlmodel import Session, select
from utils.db import crear_db, get_session
from data.models import Usuario, PeliculaSerie, Valoracion, Rutina
from routers import usuario, peliculaSerie, valoracion, rutina, web
import images
from sqlalchemy import func, desc

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

    # --- Lógica: Obtener 5 Títulos Mejor Valorados ---
    ratings_grouped_by_title_query = (
        select(
            PeliculaSerie.id_titulo,
            PeliculaSerie.titulo,
            PeliculaSerie.img.label("img_url"),
            func.avg(Valoracion.puntuacion).label("promedio_puntuacion"),
        )
        .join(Valoracion, PeliculaSerie.id_titulo == Valoracion.id_titulo_FK)
        .where(PeliculaSerie.is_active == True, Valoracion.is_active == True)
        .group_by(PeliculaSerie.id_titulo, PeliculaSerie.titulo, PeliculaSerie.img)
        .order_by(desc("promedio_puntuacion"))
        .limit(5)
    )

    top_rated_results = session.exec(ratings_grouped_by_title_query).all()

    top_titles = []
    for row in top_rated_results:
        # Redondeo en Python
        promedio_puntuacion_rounded = round(row[3], 1) if row[3] is not None else 0.0

        top_titles.append({
            "titulo": row[1],
            "img_url": row[2] if row[2] else '/static/img/placeholder_movie.jpg',
            "promedio_puntuacion": promedio_puntuacion_rounded,
        })
    # --- FIN Lógica ---

    return templates.TemplateResponse("index.html", {
        "request": request,
        "n_usuarios": n_usuarios,
        "n_titulos": n_titulos,
        "n_valoraciones": n_valoraciones,
        "n_rutinas": n_rutinas,
        "top_titles": top_titles
    })

app.include_router(web.router)
app.include_router(usuario.router)
app.include_router(peliculaSerie.router)
app.include_router(valoracion.router)
app.include_router(rutina.router)