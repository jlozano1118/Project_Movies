from fastapi import APIRouter, Request, Depends, Form
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from sqlmodel import Session, select
from datetime import date, datetime
from typing import Optional

from utils.db import get_session
from utils.security import get_password_hash
from data.models import Usuario, PeliculaSerie, Valoracion, Rutina

router = APIRouter(
    prefix="/web",
    tags=["Web Interface"]
)

templates = Jinja2Templates(directory="templates")

# ==========================================
# GESTIÓN DE USUARIOS
# ==========================================

@router.get("/usuarios", response_class=HTMLResponse)
async def pagina_usuarios(request: Request, session: Session = Depends(get_session)):
    activos = session.exec(select(Usuario).where(Usuario.is_active == True)).all()
    inactivos = session.exec(select(Usuario).where(Usuario.is_active == False)).all()
    return templates.TemplateResponse("usuarios.html", {"request": request, "usuarios_activos": activos, "usuarios_inactivos": inactivos})

@router.get("/usuarios/crear", response_class=HTMLResponse)
async def pagina_crear_usuario(request: Request):
    return templates.TemplateResponse("usuario_form.html", {"request": request, "accion": "Crear", "usuario": None})

@router.post("/usuarios/crear")
async def crear_usuario_web(nombre: str = Form(...), correo: str = Form(...), clave: str = Form(...), session: Session = Depends(get_session)):
    clave_hash = get_password_hash(clave)
    nuevo_usuario = Usuario(nombre=nombre, correo=correo, clave=clave_hash)
    session.add(nuevo_usuario)
    session.commit()
    return RedirectResponse(url="/web/usuarios?mensaje=Usuario creado correctamente", status_code=303)

@router.get("/usuarios/editar/{id_usuario}", response_class=HTMLResponse)
async def pagina_editar_usuario(id_usuario: int, request: Request, session: Session = Depends(get_session)):
    usuario = session.get(Usuario, id_usuario)
    return templates.TemplateResponse("usuario_form.html", {"request": request, "accion": "Editar", "usuario": usuario})

@router.post("/usuarios/editar/{id_usuario}")
async def editar_usuario_web(id_usuario: int, nombre: str = Form(...), correo: str = Form(...), clave: Optional[str] = Form(None), session: Session = Depends(get_session)):
    usuario = session.get(Usuario, id_usuario)
    usuario.nombre = nombre
    usuario.correo = correo
    if clave and clave.strip() != "":
        usuario.clave = get_password_hash(clave)
    session.commit()
    return RedirectResponse(url="/web/usuarios?mensaje=Usuario actualizado correctamente", status_code=303)

@router.get("/usuarios/eliminar/{id_usuario}")
async def eliminar_usuario_web(id_usuario: int, session: Session = Depends(get_session)):
    usuario = session.get(Usuario, id_usuario)
    if usuario:
        usuario.is_active = False
        usuario.deleted_at = datetime.now()
        session.commit()
    return RedirectResponse(url="/web/usuarios?mensaje=Usuario movido a inactivos", status_code=303)

@router.get("/usuarios/restaurar/{id_usuario}")
async def restaurar_usuario_web(id_usuario: int, session: Session = Depends(get_session)):
    usuario = session.get(Usuario, id_usuario)
    if usuario:
        usuario.is_active = True
        usuario.deleted_at = None
        session.commit()
    return RedirectResponse(url="/web/usuarios?mensaje=Usuario reactivado correctamente", status_code=303)


# ==========================================
# GESTIÓN DE TÍTULOS
# ==========================================

@router.get("/titulos", response_class=HTMLResponse)
async def pagina_titulos(request: Request, session: Session = Depends(get_session)):
    activos = session.exec(select(PeliculaSerie).where(PeliculaSerie.is_active == True)).all()
    inactivos = session.exec(select(PeliculaSerie).where(PeliculaSerie.is_active == False)).all()
    return templates.TemplateResponse("titulos.html", {"request": request, "titulos_activos": activos, "titulos_inactivos": inactivos})

@router.get("/titulos/crear", response_class=HTMLResponse)
async def pagina_crear_titulo(request: Request):
    return templates.TemplateResponse("titulo_form.html", {"request": request, "accion": "Crear", "titulo": None})

@router.post("/titulos/crear")
async def crear_titulo_web(titulo: str = Form(...), genero: str = Form(...), anio_estreno: int = Form(...), duracion: int = Form(...), descripcion: str = Form(...), session: Session = Depends(get_session)):
    nuevo_titulo = PeliculaSerie(titulo=titulo, genero=genero, anio_estreno=anio_estreno, duracion=duracion, descripcion=descripcion)
    session.add(nuevo_titulo)
    session.commit()
    return RedirectResponse(url="/web/titulos?mensaje=Título creado correctamente", status_code=303)

@router.get("/titulos/editar/{id_titulo}", response_class=HTMLResponse)
async def pagina_editar_titulo(id_titulo: int, request: Request, session: Session = Depends(get_session)):
    titulo = session.get(PeliculaSerie, id_titulo)
    return templates.TemplateResponse("titulo_form.html", {"request": request, "accion": "Editar", "titulo": titulo})

@router.post("/titulos/editar/{id_titulo}")
async def editar_titulo_web(id_titulo: int, titulo: str = Form(...), genero: str = Form(...), anio_estreno: int = Form(...), duracion: int = Form(...), descripcion: str = Form(...), session: Session = Depends(get_session)):
    titulo_obj = session.get(PeliculaSerie, id_titulo)
    titulo_obj.titulo = titulo
    titulo_obj.genero = genero
    titulo_obj.anio_estreno = anio_estreno
    titulo_obj.duracion = duracion
    titulo_obj.descripcion = descripcion
    session.commit()
    return RedirectResponse(url="/web/titulos?mensaje=Título actualizado correctamente", status_code=303)

@router.get("/titulos/eliminar/{id_titulo}")
async def eliminar_titulo_web(id_titulo: int, session: Session = Depends(get_session)):
    titulo = session.get(PeliculaSerie, id_titulo)
    if titulo:
        titulo.is_active = False
        titulo.deleted_at = datetime.now()
        session.commit()
    return RedirectResponse(url="/web/titulos?mensaje=Título movido a inactivos", status_code=303)

@router.get("/titulos/restaurar/{id_titulo}")
async def restaurar_titulo_web(id_titulo: int, session: Session = Depends(get_session)):
    titulo = session.get(PeliculaSerie, id_titulo)
    if titulo:
        titulo.is_active = True
        titulo.deleted_at = None
        session.commit()
    return RedirectResponse(url="/web/titulos?mensaje=Título reactivado correctamente", status_code=303)


# ==========================================
# GESTIÓN DE VALORACIONES (ACTUALIZADO)
# ==========================================

@router.get("/valoraciones", response_class=HTMLResponse)
async def pagina_valoraciones(request: Request, session: Session = Depends(get_session)):
    # 1. Separar listas
    activas = session.exec(select(Valoracion).where(Valoracion.is_active == True)).all()
    inactivas = session.exec(select(Valoracion).where(Valoracion.is_active == False)).all()
    
    # 2. Diccionarios para mostrar nombres
    usuarios = session.exec(select(Usuario)).all()
    titulos = session.exec(select(PeliculaSerie)).all()
    usuarios_dict = {u.id_usuario: u for u in usuarios}
    titulos_dict = {t.id_titulo: t for t in titulos}
    
    return templates.TemplateResponse("valoraciones.html", {
        "request": request, 
        "valoraciones_activas": activas,
        "valoraciones_inactivas": inactivas,
        "usuarios_dict": usuarios_dict, 
        "titulos_dict": titulos_dict
    })

@router.get("/valoraciones/crear", response_class=HTMLResponse)
async def pagina_crear_valoracion(request: Request, session: Session = Depends(get_session)):
    usuarios = session.exec(select(Usuario).where(Usuario.is_active == True)).all()
    titulos = session.exec(select(PeliculaSerie).where(PeliculaSerie.is_active == True)).all()
    return templates.TemplateResponse("valoracion_form.html", {
        "request": request, "accion": "Crear", "valoracion": None,
        "usuarios": usuarios, "titulos": titulos
    })

@router.post("/valoraciones/crear")
async def crear_valoracion_web(
    id_usuario_FK: int = Form(...), id_titulo_FK: int = Form(...),
    puntuacion: float = Form(...), comentario: str = Form(...),
    fecha: str = Form(...), session: Session = Depends(get_session)
):
    fecha_obj = datetime.strptime(fecha, "%Y-%m-%d").date()
    nueva_val = Valoracion(id_usuario_FK=id_usuario_FK, id_titulo_FK=id_titulo_FK, puntuacion=puntuacion, comentario=comentario, fecha=fecha_obj)
    session.add(nueva_val)
    session.commit()
    return RedirectResponse(url="/web/valoraciones?mensaje=Valoración registrada", status_code=303)

@router.get("/valoraciones/editar/{id_valoracion}", response_class=HTMLResponse)
async def pagina_editar_valoracion(id_valoracion: int, request: Request, session: Session = Depends(get_session)):
    valoracion = session.get(Valoracion, id_valoracion)
    # Necesitamos las listas para los Selects
    usuarios = session.exec(select(Usuario).where(Usuario.is_active == True)).all()
    titulos = session.exec(select(PeliculaSerie).where(PeliculaSerie.is_active == True)).all()
    
    return templates.TemplateResponse("valoracion_form.html", {
        "request": request, "accion": "Editar", "valoracion": valoracion,
        "usuarios": usuarios, "titulos": titulos
    })

@router.post("/valoraciones/editar/{id_valoracion}")
async def editar_valoracion_web(
    id_valoracion: int,
    id_usuario_FK: int = Form(...), id_titulo_FK: int = Form(...),
    puntuacion: float = Form(...), comentario: str = Form(...),
    fecha: str = Form(...), session: Session = Depends(get_session)
):
    val = session.get(Valoracion, id_valoracion)
    val.id_usuario_FK = id_usuario_FK
    val.id_titulo_FK = id_titulo_FK
    val.puntuacion = puntuacion
    val.comentario = comentario
    val.fecha = datetime.strptime(fecha, "%Y-%m-%d").date()
    
    session.commit()
    return RedirectResponse(url="/web/valoraciones?mensaje=Valoración actualizada", status_code=303)

@router.get("/valoraciones/eliminar/{id_valoracion}")
async def eliminar_valoracion_web(id_valoracion: int, session: Session = Depends(get_session)):
    val = session.get(Valoracion, id_valoracion)
    if val:
        val.is_active = False
        val.deleted_at = datetime.now()
        session.commit()
    return RedirectResponse(url="/web/valoraciones?mensaje=Valoración movida a papelera", status_code=303)

@router.get("/valoraciones/restaurar/{id_valoracion}")
async def restaurar_valoracion_web(id_valoracion: int, session: Session = Depends(get_session)):
    val = session.get(Valoracion, id_valoracion)
    if val:
        val.is_active = True
        val.deleted_at = None
        session.commit()
    return RedirectResponse(url="/web/valoraciones?mensaje=Valoración restaurada", status_code=303)


# ==========================================
# GESTIÓN DE RUTINAS
# ==========================================

@router.get("/rutinas", response_class=HTMLResponse)
async def pagina_rutinas(request: Request, session: Session = Depends(get_session)):
    rutinas = session.exec(select(Rutina).where(Rutina.is_active == True)).all()
    usuarios = session.exec(select(Usuario)).all()
    titulos = session.exec(select(PeliculaSerie)).all()
    usuarios_dict = {u.id_usuario: u for u in usuarios}
    titulos_dict = {t.id_titulo: t for t in titulos}
    return templates.TemplateResponse("rutinas.html", {"request": request, "rutinas": rutinas, "usuarios_dict": usuarios_dict, "titulos_dict": titulos_dict})

@router.get("/rutinas/crear", response_class=HTMLResponse)
async def pagina_crear_rutina(request: Request, session: Session = Depends(get_session)):
    usuarios = session.exec(select(Usuario).where(Usuario.is_active == True)).all()
    titulos = session.exec(select(PeliculaSerie).where(PeliculaSerie.is_active == True)).all()
    return templates.TemplateResponse("rutina_form.html", {"request": request, "accion": "Crear", "rutina": None, "usuarios": usuarios, "titulos": titulos})

@router.post("/rutinas/crear")
async def crear_rutina_web(nombre: str = Form(...), id_usuario_FK: int = Form(...), id_titulo_FK: int = Form(...), fecha_inicio: str = Form(...), fecha_fin: str = Form(...), session: Session = Depends(get_session)):
    rutina = Rutina(nombre=nombre, id_usuario_FK=id_usuario_FK, id_titulo_FK=id_titulo_FK, fecha_inicio=datetime.strptime(fecha_inicio, "%Y-%m-%d").date(), fecha_fin=datetime.strptime(fecha_fin, "%Y-%m-%d").date())
    session.add(rutina)
    session.commit()
    return RedirectResponse(url="/web/rutinas?mensaje=Rutina creada", status_code=303)

@router.get("/rutinas/eliminar/{id_rutina}")
async def eliminar_rutina_web(id_rutina: int, session: Session = Depends(get_session)):
    rutina = session.get(Rutina, id_rutina)
    if rutina:
        rutina.is_active = False
        rutina.deleted_at = datetime.now()
        session.commit()
    return RedirectResponse(url="/web/rutinas?mensaje=Rutina eliminada", status_code=303)
