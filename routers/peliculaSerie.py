from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import Session, select
from typing import List
from datetime import datetime
from utils.db import get_session
from data.models import PeliculaSerie, PeliculaSerieCreate

router = APIRouter(
    prefix="/titulos",
    tags=["Películas y Series"]
)


@router.post("/", response_model=PeliculaSerie, summary="Crear una nueva película o serie")
def crear_titulo(titulo: PeliculaSerieCreate, session: Session = Depends(get_session)):
    existente = session.exec(select(PeliculaSerie).where(PeliculaSerie.titulo == titulo.titulo)).first()
    if existente:
        raise HTTPException(status_code=400, detail=f"Ya existe un título con el nombre {titulo.titulo}")

    titulo_obj = PeliculaSerie(**titulo.dict())
    session.add(titulo_obj)
    session.commit()
    session.refresh(titulo_obj)
    return titulo_obj


@router.get("/", response_model=List[PeliculaSerie], summary="Listar todas las películas/series")
def listar_titulos(session: Session = Depends(get_session)):
    titulos = session.exec(select(PeliculaSerie).where(PeliculaSerie.is_active == True)).all()
    return titulos or []


@router.get("/eliminados", response_model=List[PeliculaSerie], summary="Listar películas/series eliminadas")
def listar_titulos_eliminados(session: Session = Depends(get_session)):
    eliminados = session.exec(select(PeliculaSerie).where(PeliculaSerie.is_active == False)).all()
    return eliminados or []


@router.get("/nombre/{titulo_nombre}", response_model=PeliculaSerie, summary="Obtener película o serie por nombre")
def buscar_titulo_por_nombre(titulo_nombre: str, session: Session = Depends(get_session)):
    titulo = session.exec(select(PeliculaSerie).where(PeliculaSerie.titulo == titulo_nombre, PeliculaSerie.is_active == True)).first()
    if not titulo:
        raise HTTPException(status_code=404, detail=f"No se encontró el título {titulo_nombre}")
    return titulo


@router.get("/{id_titulo}", response_model=PeliculaSerie, summary="Obtener película o serie por ID")
def ver_titulo(id_titulo: int, session: Session = Depends(get_session)):
    titulo = session.get(PeliculaSerie, id_titulo)
    if not titulo or not titulo.is_active:
        raise HTTPException(status_code=404, detail=f"Título con ID {id_titulo} no encontrado o inactivo")

    _ = titulo.valoraciones
    _ = titulo.rutinas
    return titulo


@router.put("/{id_titulo}", response_model=PeliculaSerie, summary="Actualizar una película o serie")
def actualizar_titulo(id_titulo: int, datos: PeliculaSerieCreate, session: Session = Depends(get_session)):
    titulo = session.get(PeliculaSerie, id_titulo)
    if not titulo or not titulo.is_active:
        raise HTTPException(status_code=404, detail=f"Título con ID {id_titulo} no encontrado o inactivo")

    titulo.titulo = datos.titulo
    titulo.genero = datos.genero
    titulo.anio_estreno = datos.anio_estreno
    titulo.duracion = datos.duracion
    titulo.descripcion = datos.descripcion

    session.commit()
    session.refresh(titulo)
    return titulo


@router.delete("/{id_titulo}", response_model=dict, summary="Eliminar una película o serie (lógico)")
def eliminar_titulo(id_titulo: int, session: Session = Depends(get_session)):
    titulo = session.get(PeliculaSerie, id_titulo)
    if not titulo:
        raise HTTPException(status_code=404, detail=f"Título con ID {id_titulo} no encontrado")
    titulo.is_active = False
    titulo.deleted_at = datetime.now()
    session.commit()
    return {"mensaje": f"Título con ID {id_titulo} desactivado correctamente"}