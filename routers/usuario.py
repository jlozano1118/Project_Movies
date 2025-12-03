from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import Session, select
from typing import List
from datetime import datetime
from utils.db import get_session
from data.models import Usuario, UsuarioCreate

router = APIRouter(
    prefix="/usuarios",
    tags=["Usuarios"]
)


@router.post("/", response_model=Usuario, summary="Crear un nuevo usuario")
def crear_nuevo_usuario(usuario: UsuarioCreate, session: Session = Depends(get_session)):
    existente = session.exec(select(Usuario).where(Usuario.correo == usuario.correo)).first()
    if existente:
        raise HTTPException(status_code=400, detail=f"Ya existe un usuario con el correo {usuario.correo}")

    usuario_obj = Usuario(**usuario.dict())
    session.add(usuario_obj)
    session.commit()
    session.refresh(usuario_obj)
    return usuario_obj


@router.get("/", response_model=List[Usuario], summary="Listar todos los usuarios")
def listar_usuarios(session: Session = Depends(get_session)):
    usuarios = session.exec(select(Usuario).where(Usuario.is_active == True)).all()
    return usuarios or []


@router.get("/eliminados", response_model=List[Usuario], summary="Listar usuarios eliminados")
def listar_usuarios_eliminados(session: Session = Depends(get_session)):
    eliminados = session.exec(select(Usuario).where(Usuario.is_active == False)).all()
    return eliminados or []


@router.get("/correo/{correo}", response_model=Usuario, summary="Obtener usuario por correo")
def buscar_usuario_por_correo(correo: str, session: Session = Depends(get_session)):
    usuario = session.exec(select(Usuario).where(Usuario.correo == correo, Usuario.is_active == True)).first()
    if not usuario:
        raise HTTPException(status_code=404, detail=f"No se encontró usuario con correo {correo}")
    return usuario


@router.get("/{id_usuario}", response_model=Usuario, summary="Obtener un usuario por ID")
def ver_usuario(id_usuario: int, session: Session = Depends(get_session)):
    usuario = session.get(Usuario, id_usuario)
    if not usuario or not usuario.is_active:
        raise HTTPException(status_code=404, detail=f"Usuario con ID {id_usuario} no encontrado o inactivo")

    _ = usuario.valoraciones
    _ = usuario.rutinas
    return usuario


@router.put("/{id_usuario}", response_model=Usuario, summary="Actualizar un usuario")
def actualizar_usuario(id_usuario: int, datos: UsuarioCreate, session: Session = Depends(get_session)):
    usuario = session.get(Usuario, id_usuario)
    if not usuario or not usuario.is_active:
        raise HTTPException(status_code=404, detail=f"Usuario con ID {id_usuario} no encontrado o inactivo")

    if datos.correo != usuario.correo:
        existente = session.exec(select(Usuario).where(Usuario.correo == datos.correo)).first()
        if existente:
            raise HTTPException(status_code=400, detail=f"El correo {datos.correo} ya está en uso")

    usuario.nombre = datos.nombre
    usuario.correo = datos.correo
    usuario.clave = datos.clave

    session.commit()
    session.refresh(usuario)
    return usuario


@router.delete("/{id_usuario}", response_model=dict, summary="Eliminar un usuario (lógico)")
def eliminar_usuario(id_usuario: int, session: Session = Depends(get_session)):
    usuario = session.get(Usuario, id_usuario)
    if not usuario:
        raise HTTPException(status_code=404, detail=f"Usuario con ID {id_usuario} no encontrado")
    usuario.is_active = False
    usuario.deleted_at = datetime.now()
    session.commit()
    return {"mensaje": f"Usuario con ID {id_usuario} desactivado correctamente"}