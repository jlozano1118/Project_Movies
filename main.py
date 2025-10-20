from fastapi import FastAPI, Depends, HTTPException
from sqlmodel import Session, select
from typing import List
from utils.db import engine, crear_db, get_session
from data.models import Usuario, PeliculaSerie, Valoracion, Rutina
from operations.operations import (
    crear_usuario,
    obtener_usuarios,
    obtener_usuario_por_id,
    actualizar_usuario,
    eliminar_usuario,
    crear_titulo,
    obtener_titulos,
    obtener_titulo_por_id,
    actualizar_titulo,
    eliminar_titulo,
    crear_valoracion,
    obtener_valoraciones,
    obtener_valoracion_por_id,
    actualizar_valoracion,
    eliminar_valoracion,
    crear_rutina,
    obtener_rutinas,
    obtener_rutina_por_id,
    actualizar_rutina,
    eliminar_rutina
)


app = FastAPI(
    title="API de Gestión de Películas, Valoraciones y Rutinas",
    description="API para gestionar usuarios, películas/series, valoraciones y rutinas",
)

@app.get("/")
def root():
    return {"mensaje": "Bienvenido a la API de gestión de películas y usuarios"}


@app.on_event("startup")
def startup():
    crear_db()


@app.post("/usuarios/", response_model=Usuario, summary="Crear un nuevo usuario")
def crear_nuevo_usuario(usuario: Usuario, session: Session = Depends(get_session)):
    return crear_usuario(session, usuario)


@app.get("/usuarios/", response_model=List[Usuario], summary="Listar todos los usuarios")
def listar_usuarios(session: Session = Depends(get_session)):
    return obtener_usuarios(session)


@app.get("/usuarios/{id_usuario}", response_model=Usuario, summary="Obtener un usuario por ID")
def ver_usuario(id_usuario: int, session: Session = Depends(get_session)):
    return obtener_usuario_por_id(session, id_usuario)


@app.put("/usuarios/{id_usuario}", response_model=Usuario, summary="Actualizar un usuario")
def actualizar_usuario_endpoint(id_usuario: int, datos: Usuario, session: Session = Depends(get_session)):
    return actualizar_usuario(session, id_usuario, datos)


@app.delete("/usuarios/{id_usuario}", response_model=Usuario, summary="Eliminar un usuario")
def eliminar_usuario_endpoint(id_usuario: int, session: Session = Depends(get_session)):
    return eliminar_usuario(session, id_usuario)



@app.post("/titulos/", response_model=PeliculaSerie, summary="Crear una nueva película o serie")
def crear_titulo_endpoint(titulo: PeliculaSerie, session: Session = Depends(get_session)):
    return crear_titulo(session, titulo)


@app.get("/titulos/", response_model=List[PeliculaSerie], summary="Listar todas las películas/series")
def listar_titulos(session: Session = Depends(get_session)):
    return obtener_titulos(session)


@app.get("/titulos/{id_titulo}", response_model=PeliculaSerie, summary="Obtener película o serie por ID")
def ver_titulo(id_titulo: int, session: Session = Depends(get_session)):
    return obtener_titulo_por_id(session, id_titulo)


@app.put("/titulos/{id_titulo}", response_model=PeliculaSerie, summary="Actualizar una película o serie")
def actualizar_titulo_endpoint(id_titulo: int, datos: PeliculaSerie, session: Session = Depends(get_session)):
    return actualizar_titulo(session, id_titulo, datos)


@app.delete("/titulos/{id_titulo}", response_model=PeliculaSerie, summary="Eliminar una película o serie")
def eliminar_titulo_endpoint(id_titulo: int, session: Session = Depends(get_session)):
    return eliminar_titulo(session, id_titulo)



@app.post("/valoraciones/", response_model=Valoracion, summary="Crear una nueva valoración")
def crear_valoracion_endpoint(valoracion: Valoracion, session: Session = Depends(get_session)):
    return crear_valoracion(session, valoracion)


@app.get("/valoraciones/", response_model=List[Valoracion], summary="Listar todas las valoraciones")
def listar_valoraciones(session: Session = Depends(get_session)):
    return obtener_valoraciones(session)


@app.get("/valoraciones/{id_valoracion}", response_model=Valoracion, summary="Obtener valoración por ID")
def ver_valoracion(id_valoracion: int, session: Session = Depends(get_session)):
    return obtener_valoracion_por_id(session, id_valoracion)


@app.put("/valoraciones/{id_valoracion}", response_model=Valoracion, summary="Actualizar una valoración")
def actualizar_valoracion_endpoint(id_valoracion: int, datos: Valoracion, session: Session = Depends(get_session)):
    return actualizar_valoracion(session, id_valoracion, datos)


@app.delete("/valoraciones/{id_valoracion}", response_model=dict, summary="Eliminar una valoración")
def eliminar_valoracion_endpoint(id_valoracion: int, session: Session = Depends(get_session)):
    return eliminar_valoracion(session, id_valoracion)



@app.post("/rutinas/", response_model=Rutina, summary="Crear una nueva rutina")
def crear_rutina_endpoint(rutina: Rutina, session: Session = Depends(get_session)):
    return crear_rutina(session, rutina)


@app.get("/rutinas/", response_model=List[Rutina], summary="Listar todas las rutinas")
def listar_rutinas(session: Session = Depends(get_session)):
    return obtener_rutinas(session)


@app.get("/rutinas/{id_rutina}", response_model=Rutina, summary="Obtener rutina por ID")
def ver_rutina(id_rutina: int, session: Session = Depends(get_session)):
    return obtener_rutina_por_id(session, id_rutina)


@app.put("/rutinas/{id_rutina}", response_model=Rutina, summary="Actualizar una rutina")
def actualizar_rutina_endpoint(id_rutina: int, datos: Rutina, session: Session = Depends(get_session)):
    return actualizar_rutina(session, id_rutina, datos)


@app.delete("/rutinas/{id_rutina}", response_model=dict, summary="Eliminar una rutina")
def eliminar_rutina_endpoint(id_rutina: int, session: Session = Depends(get_session)):
    return eliminar_rutina(session, id_rutina)
