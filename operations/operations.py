from sqlmodel import Session, select
from fastapi import HTTPException, status
from datetime import datetime, date
from data.models import Usuario, PeliculaSerie, Valoracion, Rutina


# -------------------- USUARIOS --------------------
def crear_usuario(session: Session, usuario: Usuario):
    existente = session.exec(select(Usuario).where(Usuario.correo == usuario.correo)).first()
    if existente:
        raise HTTPException(status_code=400, detail=f"Ya existe un usuario con el correo {usuario.correo}")

    session.add(usuario)
    session.commit()
    session.refresh(usuario)
    return usuario


def obtener_usuarios(session: Session):
    usuarios = session.exec(select(Usuario).where(Usuario.is_active == True)).all()
    return usuarios or []


def obtener_usuario_por_id(session: Session, id_usuario: int):
    usuario = session.get(Usuario, id_usuario)
    if not usuario or not usuario.is_active:
        raise HTTPException(status_code=404, detail=f"Usuario con ID {id_usuario} no encontrado o inactivo")

    # Carga de relaciones
    _ = usuario.valoraciones
    _ = usuario.rutinas
    return usuario


def actualizar_usuario(session: Session, id_usuario: int, datos: Usuario):
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


def obtener_usuario_por_correo(session: Session, correo: str):
    usuario = session.exec(select(Usuario).where(Usuario.correo == correo, Usuario.is_active == True)).first()
    if not usuario:
        raise HTTPException(status_code=404, detail=f"No se encontró usuario con correo {correo}")
    return usuario


def eliminar_usuario(session: Session, id_usuario: int):
    usuario = session.get(Usuario, id_usuario)
    if not usuario:
        raise HTTPException(status_code=404, detail=f"Usuario con ID {id_usuario} no encontrado")
    usuario.is_active = False
    usuario.deleted_at = datetime.now()
    session.commit()
    return {"mensaje": f"Usuario con ID {id_usuario} desactivado correctamente"}


def obtener_usuarios_eliminados(session: Session):
    eliminados = session.exec(select(Usuario).where(Usuario.is_active == False)).all()
    return eliminados or []


# -------------------- TITULOS --------------------
def crear_titulo(session: Session, titulo: PeliculaSerie):
    existente = session.exec(select(PeliculaSerie).where(PeliculaSerie.titulo == titulo.titulo)).first()
    if existente:
        raise HTTPException(status_code=400, detail=f"Ya existe un título con el nombre {titulo.titulo}")

    session.add(titulo)
    session.commit()
    session.refresh(titulo)
    return titulo


def obtener_titulos(session: Session):
    titulos = session.exec(select(PeliculaSerie).where(PeliculaSerie.is_active == True)).all()
    return titulos or []


def obtener_titulo_por_id(session: Session, id_titulo: int):
    titulo = session.get(PeliculaSerie, id_titulo)
    if not titulo or not titulo.is_active:
        raise HTTPException(status_code=404, detail=f"Título con ID {id_titulo} no encontrado o inactivo")

    _ = titulo.valoraciones
    _ = titulo.rutinas
    return titulo


def actualizar_titulo(session: Session, id_titulo: int, datos: PeliculaSerie):
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


def obtener_titulo_por_nombre(session: Session, titulo_nombre: str):
    titulo = session.exec(select(PeliculaSerie).where(PeliculaSerie.titulo == titulo_nombre, PeliculaSerie.is_active == True)).first()
    if not titulo:
        raise HTTPException(status_code=404, detail=f"No se encontró el título {titulo_nombre}")
    return titulo


def eliminar_titulo(session: Session, id_titulo: int):
    titulo = session.get(PeliculaSerie, id_titulo)
    if not titulo:
        raise HTTPException(status_code=404, detail=f"Título con ID {id_titulo} no encontrado")
    titulo.is_active = False
    titulo.deleted_at = datetime.now()
    session.commit()
    return {"mensaje": f"Título con ID {id_titulo} desactivado correctamente"}


def obtener_titulos_eliminados(session: Session):
    eliminados = session.exec(select(PeliculaSerie).where(PeliculaSerie.is_active == False)).all()
    return eliminados or []


# -------------------- VALORACIONES --------------------
def crear_valoracion(session: Session, valoracion: Valoracion):
    usuario = session.get(Usuario, valoracion.id_usuario_FK)
    titulo = session.get(PeliculaSerie, valoracion.id_titulo_FK)

    if not usuario or not usuario.is_active:
        raise HTTPException(status_code=404, detail=f"Usuario con ID {valoracion.id_usuario_FK} no encontrado o inactivo")
    if not titulo or not titulo.is_active:
        raise HTTPException(status_code=404, detail=f"Título con ID {valoracion.id_titulo_FK} no encontrado o inactivo")

    session.add(valoracion)
    session.commit()
    session.refresh(valoracion)
    return valoracion


def obtener_valoraciones(session: Session):
    valoraciones = session.exec(select(Valoracion).where(Valoracion.is_active == True)).all()
    return valoraciones or []


def obtener_valoracion_por_id(session: Session, id_valoracion: int):
    valoracion = session.get(Valoracion, id_valoracion)
    if not valoracion or not valoracion.is_active:
        raise HTTPException(status_code=404, detail=f"Valoración con ID {id_valoracion} no encontrada o inactiva")
    return valoracion


def actualizar_valoracion(session: Session, id_valoracion: int, datos: Valoracion):
    valoracion = session.get(Valoracion, id_valoracion)
    if not valoracion or not valoracion.is_active:
        raise HTTPException(status_code=404, detail=f"Valoración con ID {id_valoracion} no encontrada o inactiva")

    valoracion.puntuacion = datos.puntuacion
    valoracion.comentario = datos.comentario
    valoracion.fecha = datos.fecha

    session.commit()
    session.refresh(valoracion)
    return valoracion


def obtener_valoracion_por_comentario(session: Session, comentario: str):
    valoracion = session.exec(select(Valoracion).where(Valoracion.comentario == comentario, Valoracion.is_active == True)).first()
    if not valoracion:
        raise HTTPException(status_code=404, detail=f"No se encontró la valoración con comentario '{comentario}'")
    return valoracion


def eliminar_valoracion(session: Session, id_valoracion: int):
    valoracion = session.get(Valoracion, id_valoracion)
    if not valoracion:
        raise HTTPException(status_code=404, detail=f"Valoración con ID {id_valoracion} no encontrada")
    valoracion.is_active = False
    valoracion.deleted_at = datetime.now()
    session.commit()
    return {"mensaje": f"Valoración con ID {id_valoracion} desactivada correctamente"}


def obtener_valoraciones_eliminadas(session: Session):
    eliminadas = session.exec(select(Valoracion).where(Valoracion.is_active == False)).all()
    return eliminadas or []


# -------------------- RUTINAS --------------------
def crear_rutina(session: Session, rutina: Rutina):
    usuario = session.get(Usuario, rutina.id_usuario_FK)
    titulo = session.get(PeliculaSerie, rutina.id_titulo_FK)

    if not usuario or not usuario.is_active:
        raise HTTPException(status_code=404, detail=f"Usuario con ID {rutina.id_usuario_FK} no encontrado o inactivo")
    if not titulo or not titulo.is_active:
        raise HTTPException(status_code=404, detail=f"Título con ID {rutina.id_titulo_FK} no encontrado o inactivo")

    session.add(rutina)
    session.commit()
    session.refresh(rutina)
    return rutina


def obtener_rutinas(session: Session):
    rutinas = session.exec(select(Rutina).where(Rutina.is_active == True)).all()
    return rutinas or []


def obtener_rutina_por_id(session: Session, id_rutina: int):
    rutina = session.get(Rutina, id_rutina)
    if not rutina or not rutina.is_active:
        raise HTTPException(status_code=404, detail=f"Rutina con ID {id_rutina} no encontrada o inactiva")
    return rutina


def actualizar_rutina(session: Session, id_rutina: int, datos: Rutina):
    rutina = session.get(Rutina, id_rutina)
    if not rutina or not rutina.is_active:
        raise HTTPException(status_code=404, detail=f"Rutina con ID {id_rutina} no encontrada o inactiva")

    rutina.nombre = datos.nombre
    rutina.fecha_inicio = datos.fecha_inicio
    rutina.fecha_fin = datos.fecha_fin

    session.commit()
    session.refresh(rutina)
    return rutina


def obtener_rutina_por_nombre(session: Session, nombre: str):
    rutina = session.exec(select(Rutina).where(Rutina.nombre == nombre, Rutina.is_active == True)).first()
    if not rutina:
        raise HTTPException(status_code=404, detail=f"No se encontró la rutina con nombre '{nombre}'")
    return rutina


def eliminar_rutina(session: Session, id_rutina: int):
    rutina = session.get(Rutina, id_rutina)
    if not rutina:
        raise HTTPException(status_code=404, detail=f"Rutina con ID {id_rutina} no encontrada")
    rutina.is_active = False
    rutina.deleted_at = datetime.now()
    session.commit()
    return {"mensaje": f"Rutina con ID {id_rutina} desactivada correctamente"}


def obtener_rutinas_eliminadas(session: Session):
    eliminadas = session.exec(select(Rutina).where(Rutina.is_active == False)).all()
    return eliminadas or []
