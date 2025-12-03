from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import Session, select
from typing import List
from datetime import datetime
from utils.db import get_session
from data.models import Rutina, RutinaCreate, Usuario, PeliculaSerie

router = APIRouter(
    prefix="/rutinas",
    tags=["Rutinas"]
)


@router.post("/", response_model=Rutina, summary="Crear una nueva rutina")
def crear_rutina(rutina: RutinaCreate, session: Session = Depends(get_session)):
    usuario = session.get(Usuario, rutina.id_usuario_FK)
    titulo = session.get(PeliculaSerie, rutina.id_titulo_FK)

    if not usuario or not usuario.is_active:
        raise HTTPException(status_code=404, detail=f"Usuario con ID {rutina.id_usuario_FK} no encontrado o inactivo")
    if not titulo or not titulo.is_active:
        raise HTTPException(status_code=404, detail=f"Título con ID {rutina.id_titulo_FK} no encontrado o inactivo")

    rutina_obj = Rutina(**rutina.dict())
    session.add(rutina_obj)
    session.commit()
    session.refresh(rutina_obj)
    return rutina_obj


@router.get("/", response_model=List[Rutina], summary="Listar todas las rutinas")
def listar_rutinas(session: Session = Depends(get_session)):
    rutinas = session.exec(select(Rutina).where(Rutina.is_active == True)).all()
    return rutinas or []


@router.get("/eliminadas", response_model=List[Rutina], summary="Listar rutinas eliminadas")
def listar_rutinas_eliminadas(session: Session = Depends(get_session)):
    eliminadas = session.exec(select(Rutina).where(Rutina.is_active == False)).all()
    return eliminadas or []


@router.get("/nombre/{nombre}", response_model=Rutina, summary="Obtener rutina por nombre")
def buscar_rutina_por_nombre(nombre: str, session: Session = Depends(get_session)):
    rutina = session.exec(select(Rutina).where(Rutina.nombre == nombre, Rutina.is_active == True)).first()
    if not rutina:
        raise HTTPException(status_code=404, detail=f"No se encontró la rutina con nombre '{nombre}'")
    return rutina


@router.get("/{id_rutina}", response_model=Rutina, summary="Obtener rutina por ID")
def ver_rutina(id_rutina: int, session: Session = Depends(get_session)):
    rutina = session.get(Rutina, id_rutina)
    if not rutina or not rutina.is_active:
        raise HTTPException(status_code=404, detail=f"Rutina con ID {id_rutina} no encontrada o inactiva")
    return rutina


@router.put("/{id_rutina}", response_model=Rutina, summary="Actualizar una rutina")
def actualizar_rutina(id_rutina: int, datos: RutinaCreate, session: Session = Depends(get_session)):
    rutina = session.get(Rutina, id_rutina)
    if not rutina or not rutina.is_active:
        raise HTTPException(status_code=404, detail=f"Rutina con ID {id_rutina} no encontrada o inactiva")

    rutina.nombre = datos.nombre
    rutina.fecha_inicio = datos.fecha_inicio
    rutina.fecha_fin = datos.fecha_fin

    session.commit()
    session.refresh(rutina)
    return rutina


@router.delete("/{id_rutina}", response_model=dict, summary="Eliminar una rutina (lógica)")
def eliminar_rutina(id_rutina: int, session: Session = Depends(get_session)):
    rutina = session.get(Rutina, id_rutina)
    if not rutina:
        raise HTTPException(status_code=404, detail=f"Rutina con ID {id_rutina} no encontrada")
    rutina.is_active = False
    rutina.deleted_at = datetime.now()
    session.commit()
    return {"mensaje": f"Rutina con ID {id_rutina} desactivada correctamente"}