from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import Session, select
from typing import List
from datetime import datetime
from utils.db import get_session
from data.models import Valoracion, ValoracionCreate, Usuario, PeliculaSerie

router = APIRouter(
    prefix="/valoraciones",
    tags=["Valoraciones"]
)


@router.post("/", response_model=Valoracion, summary="Crear una nueva valoración")
def crear_valoracion(valoracion: ValoracionCreate, session: Session = Depends(get_session)):
    usuario = session.get(Usuario, valoracion.id_usuario_FK)
    titulo = session.get(PeliculaSerie, valoracion.id_titulo_FK)

    if not usuario or not usuario.is_active:
        raise HTTPException(status_code=404, detail=f"Usuario con ID {valoracion.id_usuario_FK} no encontrado o inactivo")
    if not titulo or not titulo.is_active:
        raise HTTPException(status_code=404, detail=f"Título con ID {valoracion.id_titulo_FK} no encontrado o inactivo")

    valoracion_obj = Valoracion(**valoracion.dict())
    session.add(valoracion_obj)
    session.commit()
    session.refresh(valoracion_obj)
    return valoracion_obj


@router.get("/", response_model=List[Valoracion], summary="Listar todas las valoraciones")
def listar_valoraciones(session: Session = Depends(get_session)):
    valoraciones = session.exec(select(Valoracion).where(Valoracion.is_active == True)).all()
    return valoraciones or []


@router.get("/eliminadas", response_model=List[Valoracion], summary="Listar valoraciones eliminadas")
def listar_valoraciones_eliminadas(session: Session = Depends(get_session)):
    eliminadas = session.exec(select(Valoracion).where(Valoracion.is_active == False)).all()
    return eliminadas or []


@router.get("/comentario/{comentario}", response_model=Valoracion, summary="Obtener valoración por comentario")
def buscar_valoracion_por_comentario(comentario: str, session: Session = Depends(get_session)):
    valoracion = session.exec(select(Valoracion).where(Valoracion.comentario == comentario, Valoracion.is_active == True)).first()
    if not valoracion:
        raise HTTPException(status_code=404, detail=f"No se encontró la valoración con comentario '{comentario}'")
    return valoracion


@router.get("/{id_valoracion}", response_model=Valoracion, summary="Obtener valoración por ID")
def ver_valoracion(id_valoracion: int, session: Session = Depends(get_session)):
    valoracion = session.get(Valoracion, id_valoracion)
    if not valoracion or not valoracion.is_active:
        raise HTTPException(status_code=404, detail=f"Valoración con ID {id_valoracion} no encontrada o inactiva")
    return valoracion


@router.put("/{id_valoracion}", response_model=Valoracion, summary="Actualizar una valoración")
def actualizar_valoracion(id_valoracion: int, datos: ValoracionCreate, session: Session = Depends(get_session)):
    valoracion = session.get(Valoracion, id_valoracion)
    if not valoracion or not valoracion.is_active:
        raise HTTPException(status_code=404, detail=f"Valoración con ID {id_valoracion} no encontrada o inactiva")

    valoracion.puntuacion = datos.puntuacion
    valoracion.comentario = datos.comentario
    valoracion.fecha = datos.fecha

    session.commit()
    session.refresh(valoracion)
    return valoracion


@router.delete("/{id_valoracion}", response_model=dict, summary="Eliminar una valoración (lógico)")
def eliminar_valoracion(id_valoracion: int, session: Session = Depends(get_session)):
    valoracion = session.get(Valoracion, id_valoracion)
    if not valoracion:
        raise HTTPException(status_code=404, detail=f"Valoración con ID {id_valoracion} no encontrada")
    valoracion.is_active = False
    valoracion.deleted_at = datetime.now()
    session.commit()
    return {"mensaje": f"Valoración con ID {id_valoracion} desactivada correctamente"}