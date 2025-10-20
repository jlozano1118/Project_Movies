from sqlmodel import Session, select
from fastapi import HTTPException, status
from datetime import date
from data.models import Usuario, PeliculaSerie, Valoracion, Rutina



def crear_usuario(session: Session, usuario: Usuario):
    existente = session.exec(select(Usuario).where(Usuario.correo == usuario.correo)).first()
    if existente:
        raise HTTPException(status_code=400, detail=f"Ya existe un usuario con el correo {usuario.correo}")

    session.add(usuario)
    session.commit()
    session.refresh(usuario)
    return usuario


def obtener_usuarios(session: Session):
    usuarios = session.exec(select(Usuario)).all()
    return usuarios or []


def obtener_usuario_por_id(session: Session, id_usuario: int):
    usuario = session.get(Usuario, id_usuario)
    if not usuario:
        raise HTTPException(status_code=404, detail=f"Usuario con ID {id_usuario} no encontrado")

    # Carga de relaciones
    _ = usuario.valoraciones
    _ = usuario.rutinas
    return usuario


def actualizar_usuario(session: Session, id_usuario: int, datos: Usuario):
    usuario = session.get(Usuario, id_usuario)
    if not usuario:
        raise HTTPException(status_code=404, detail=f"Usuario con ID {id_usuario} no encontrado")

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


def eliminar_usuario(session: Session, id_usuario: int):
    usuario = session.get(Usuario, id_usuario)
    if not usuario:
        raise HTTPException(status_code=404, detail=f"Usuario con ID {id_usuario} no encontrado")

    session.delete(usuario)
    session.commit()
    return {"mensaje": f"Usuario con ID {id_usuario} eliminado correctamente"}



def crear_titulo(session: Session, titulo: PeliculaSerie):
    existente = session.exec(select(PeliculaSerie).where(PeliculaSerie.titulo == titulo.titulo)).first()
    if existente:
        raise HTTPException(status_code=400, detail=f"Ya existe un título con el nombre {titulo.titulo}")

    session.add(titulo)
    session.commit()
    session.refresh(titulo)
    return titulo


def obtener_titulos(session: Session):
    titulos = session.exec(select(PeliculaSerie)).all()
    return titulos or []


def obtener_titulo_por_id(session: Session, id_titulo: int):
    titulo = session.get(PeliculaSerie, id_titulo)
    if not titulo:
        raise HTTPException(status_code=404, detail=f"Título con ID {id_titulo} no encontrado")


    _ = titulo.valoraciones
    _ = titulo.rutinas
    return titulo


def actualizar_titulo(session: Session, id_titulo: int, datos: PeliculaSerie):
    titulo = session.get(PeliculaSerie, id_titulo)
    if not titulo:
        raise HTTPException(status_code=404, detail=f"Título con ID {id_titulo} no encontrado")

    titulo.titulo = datos.titulo
    titulo.genero = datos.genero
    titulo.anio_estreno = datos.anio_estreno
    titulo.duracion = datos.duracion
    titulo.descripcion = datos.descripcion

    session.commit()
    session.refresh(titulo)
    return titulo


def eliminar_titulo(session: Session, id_titulo: int):
    titulo = session.get(PeliculaSerie, id_titulo)
    if not titulo:
        raise HTTPException(status_code=404, detail=f"Título con ID {id_titulo} no encontrado")

    session.delete(titulo)
    session.commit()
    return {"mensaje": f"Título con ID {id_titulo} eliminado correctamente"}



def crear_valoracion(session: Session, valoracion: Valoracion):
    usuario = session.get(Usuario, valoracion.id_usuario_FK)
    titulo = session.get(PeliculaSerie, valoracion.id_titulo_FK)

    if not usuario:
        raise HTTPException(status_code=404, detail=f"Usuario con ID {valoracion.id_usuario_FK} no encontrado")
    if not titulo:
        raise HTTPException(status_code=404, detail=f"Título con ID {valoracion.id_titulo_FK} no encontrado")

    session.add(valoracion)
    session.commit()
    session.refresh(valoracion)
    return valoracion


def obtener_valoraciones(session: Session):
    valoraciones = session.exec(select(Valoracion)).all()
    return valoraciones or []


def obtener_valoracion_por_id(session: Session, id_valoracion: int):
    valoracion = session.get(Valoracion, id_valoracion)
    if not valoracion:
        raise HTTPException(status_code=404, detail=f"Valoración con ID {id_valoracion} no encontrada")
    return valoracion


def actualizar_valoracion(session: Session, id_valoracion: int, datos: Valoracion):
    valoracion = session.get(Valoracion, id_valoracion)
    if not valoracion:
        raise HTTPException(status_code=404, detail=f"Valoración con ID {id_valoracion} no encontrada")

    valoracion.puntuacion = datos.puntuacion
    valoracion.comentario = datos.comentario
    valoracion.fecha = datos.fecha

    session.commit()
    session.refresh(valoracion)
    return valoracion


def eliminar_valoracion(session: Session, id_valoracion: int):
    valoracion = session.get(Valoracion, id_valoracion)
    if not valoracion:
        raise HTTPException(status_code=404, detail=f"Valoración con ID {id_valoracion} no encontrada")

    session.delete(valoracion)
    session.commit()
    return {"mensaje": f"Valoración con ID {id_valoracion} eliminada correctamente"}


def crear_rutina(session: Session, rutina: Rutina):
    usuario = session.get(Usuario, rutina.id_usuario_FK)
    titulo = session.get(PeliculaSerie, rutina.id_titulo_FK)

    if not usuario:
        raise HTTPException(status_code=404, detail=f"Usuario con ID {rutina.id_usuario_FK} no encontrado")
    if not titulo:
        raise HTTPException(status_code=404, detail=f"Título con ID {rutina.id_titulo_FK} no encontrado")

    session.add(rutina)
    session.commit()
    session.refresh(rutina)
    return rutina


def obtener_rutinas(session: Session):
    rutinas = session.exec(select(Rutina)).all()
    return rutinas or []


def obtener_rutina_por_id(session: Session, id_rutina: int):
    rutina = session.get(Rutina, id_rutina)
    if not rutina:
        raise HTTPException(status_code=404, detail=f"Rutina con ID {id_rutina} no encontrada")
    return rutina


def actualizar_rutina(session: Session, id_rutina: int, datos: Rutina):
    rutina = session.get(Rutina, id_rutina)
    if not rutina:
        raise HTTPException(status_code=404, detail=f"Rutina con ID {id_rutina} no encontrada")

    rutina.nombre = datos.nombre
    rutina.fecha_inicio = datos.fecha_inicio
    rutina.fecha_fin = datos.fecha_fin

    session.commit()
    session.refresh(rutina)
    return rutina


def eliminar_rutina(session: Session, id_rutina: int):
    rutina = session.get(Rutina, id_rutina)
    if not rutina:
        raise HTTPException(status_code=404, detail=f"Rutina con ID {id_rutina} no encontrada")

    session.delete(rutina)
    session.commit()
    return {"mensaje": f"Rutina con ID {id_rutina} eliminada correctamente"}
