from fastapi import APIRouter, Form, File, UploadFile, Depends, HTTPException, Request
from fastapi.responses import RedirectResponse, HTMLResponse
from sqlmodel import Session, select
from fastapi.templating import Jinja2Templates
from utils.db import get_session
from supa.supabase import upload_to_bucket
from utils.security import get_password_hash
from data.models import Usuario, PeliculaSerie, Valoracion, Rutina
from datetime import date, datetime, timedelta
import calendar
from typing import Optional

# --- Importaciones añadidas para Paginación y Estadísticas ---
from sqlalchemy import func, desc  # func para count y avg; desc para orden descendente
import math  # Para la función math.ceil

# -------------------------------------------------------------


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
    return templates.TemplateResponse("usuarios.html", {"request": request, "usuarios_activos": activos,
                                                        "usuarios_inactivos": inactivos})


@router.get("/usuarios/crear", response_class=HTMLResponse)
async def pagina_crear_usuario(request: Request):
    return templates.TemplateResponse("usuario_form.html", {"request": request, "accion": "Crear", "usuario": None})


@router.post("/usuarios/crear")
async def crear_usuario_web(
        nombre: str = Form(...),
        correo: str = Form(...),
        clave: str = Form(...),
        img: UploadFile = File(None),
        session: Session = Depends(get_session)
):
    clave_hash = get_password_hash(clave)

    img_url = None
    if img is not None:
        try:
            img_url = await upload_to_bucket(img)
        except Exception as e:
            raise HTTPException(status_code=400, detail=f"Error subiendo imagen: {str(e)}")

    try:
        nuevo_usuario = Usuario(
            nombre=nombre,
            correo=correo,
            clave=clave_hash,
            img=img_url
        )

        session.add(nuevo_usuario)
        session.commit()
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

    return RedirectResponse(
        url="/web/usuarios?mensaje=Usuario creado correctamente",
        status_code=303
    )


@router.get("/usuarios/editar/{id_usuario}", response_class=HTMLResponse)
async def pagina_editar_usuario(id_usuario: int, request: Request, session: Session = Depends(get_session)):
    usuario = session.get(Usuario, id_usuario)
    return templates.TemplateResponse("usuario_form.html", {"request": request, "accion": "Editar", "usuario": usuario})


@router.post("/usuarios/editar/{id_usuario}")
async def editar_usuario_web(id_usuario: int, nombre: str = Form(...), correo: str = Form(...),
                             clave: Optional[str] = Form(None), session: Session = Depends(get_session)):
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
# GESTIÓN DE TÍTULOS (CON PAGINACIÓN)
# ==========================================

@router.get("/titulos", response_class=HTMLResponse)
async def pagina_titulos(
        request: Request,
        page: int = 1,  # Parámetro de página
        session: Session = Depends(get_session)
):
    limit = 10  # Películas por página (10 por solicitud)
    offset = (page - 1) * limit

    # 1. Total de títulos activos para calcular el número de páginas
    total_query = select(func.count(PeliculaSerie.id_titulo)).where(PeliculaSerie.is_active == True)
    total_titulos = session.exec(total_query).one()
    total_pages = math.ceil(total_titulos / limit)

    # 2. Obtener títulos paginados
    query = select(PeliculaSerie).where(PeliculaSerie.is_active == True).offset(offset).limit(limit)
    activos = session.exec(query).all()

    # Inactivos (Estos se mantienen igual, sin paginación)
    inactivos = session.exec(select(PeliculaSerie).where(PeliculaSerie.is_active == False)).all()

    return templates.TemplateResponse("titulos.html", {
        "request": request,
        "titulos_activos": activos,
        "titulos_inactivos": inactivos,
        "current_page": page,
        "total_pages": total_pages
    })


@router.get("/titulos/crear", response_class=HTMLResponse)
async def pagina_crear_titulo(request: Request):
    return templates.TemplateResponse("titulo_form.html", {"request": request, "accion": "Crear", "titulo": None})


@router.post("/titulos/crear")
async def crear_titulo_web(
        titulo: str = Form(...),
        genero: str = Form(...),
        anio_estreno: int = Form(...),
        duracion: int = Form(...),
        descripcion: str = Form(...),
        img: UploadFile = File(None),
        session: Session = Depends(get_session)
):
    img_url = None
    if img is not None:
        try:
            img_url = await upload_to_bucket(img)
        except Exception as e:
            raise HTTPException(
                status_code=400,
                detail=f"Error subiendo imagen: {str(e)}"
            )

    try:
        nuevo_titulo = PeliculaSerie(
            titulo=titulo,
            genero=genero,
            anio_estreno=anio_estreno,
            duracion=duracion,
            descripcion=descripcion,
            img=img_url
        )

        session.add(nuevo_titulo)
        session.commit()

    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

    return RedirectResponse(
        url="/web/titulos?mensaje=Título creado correctamente",
        status_code=303
    )


@router.get("/titulos/editar/{id_titulo}", response_class=HTMLResponse)
async def pagina_editar_titulo(id_titulo: int, request: Request, session: Session = Depends(get_session)):
    titulo = session.get(PeliculaSerie, id_titulo)
    return templates.TemplateResponse("titulo_form.html", {"request": request, "accion": "Editar", "titulo": titulo})


@router.post("/titulos/editar/{id_titulo}")
async def editar_titulo_web(id_titulo: int, titulo: str = Form(...), genero: str = Form(...),
                            anio_estreno: int = Form(...), duracion: int = Form(...), descripcion: str = Form(...),
                            session: Session = Depends(get_session)):
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
# GESTIÓN DE VALORACIONES
# ==========================================

@router.get("/valoraciones", response_class=HTMLResponse)
async def pagina_valoraciones(request: Request, session: Session = Depends(get_session)):
    # Se obtienen todos los usuarios y títulos para la "Papelera" y para mapear en el modal
    inactivas = session.exec(select(Valoracion).where(Valoracion.is_active == False)).all()
    usuarios_dict = {u.id_usuario: u for u in session.exec(select(Usuario)).all()}
    titulos_dict = {t.id_titulo: t for t in session.exec(select(PeliculaSerie)).all()}

    # --- 2. Títulos con Valoraciones Activas (Datos Agregados) ---
    # Consulta para obtener título, imagen y la puntuación promedio (SIN REDONDEAR AQUI)
    ratings_grouped_by_title_query = (
        select(
            PeliculaSerie.id_titulo,
            PeliculaSerie.titulo,
            PeliculaSerie.img.label("img_url"),
            func.avg(Valoracion.puntuacion).label("promedio_puntuacion"),  # Eliminado func.round para evitar error
            func.count(Valoracion.id_valoracion).label("total_valoraciones")
        )
        .join(Valoracion, PeliculaSerie.id_titulo == Valoracion.id_titulo_FK)
        .where(PeliculaSerie.is_active == True, Valoracion.is_active == True)
        .group_by(PeliculaSerie.id_titulo, PeliculaSerie.titulo, PeliculaSerie.img)
        .order_by(desc("promedio_puntuacion"))
    )

    titulos_con_rating_results = session.exec(ratings_grouped_by_title_query).all()

    # Convertir los resultados agregados a una lista de diccionarios para el template
    titulos_con_rating = []
    for row in titulos_con_rating_results:
        # REDONDEO EN PYTHON para evitar el error de enlace de parámetros SQL
        promedio_puntuacion_rounded = round(row[3], 1) if row[3] is not None else 0.0

        titulos_con_rating.append({
            "id_titulo": row[0],
            "titulo": row[1],
            "img_url": row[2] if row[2] else '/static/img/placeholder_movie.jpg',
            "promedio_puntuacion": promedio_puntuacion_rounded,  # Se usa el valor redondeado
            "total_valoraciones": row[4]
        })

    # --- 3. Todas las Valoraciones Activas Agrupadas por Título (para el Modal) ---
    all_active_valoraciones = session.exec(select(Valoracion).where(Valoracion.is_active == True)).all()

    # Agrupar las valoraciones por título en Python, inyectando datos de usuario para el modal
    valoraciones_por_titulo = {}
    for val in all_active_valoraciones:
        title_id = val.id_titulo_FK
        if title_id not in valoraciones_por_titulo:
            valoraciones_por_titulo[title_id] = []

        # Obtener información de usuario del diccionario (eficiente)
        usuario_info = usuarios_dict.get(val.id_usuario_FK)

        valoraciones_por_titulo[title_id].append({
            "id_valoracion": val.id_valoracion,
            "puntuacion": val.puntuacion,
            "comentario": val.comentario,
            "fecha": val.fecha.strftime("%Y-%m-%d"),
            "usuario_nombre": usuario_info.nombre if usuario_info else 'N/A',
            "usuario_img": usuario_info.img if usuario_info and usuario_info.img else '/static/img/user-placeholder.png',
            "id_usuario_FK": val.id_usuario_FK
        })

    # --- 4. Renderizar Template ---
    return templates.TemplateResponse("valoraciones.html", {
        "request": request,
        "titulos_con_rating": titulos_con_rating,
        "valoraciones_por_titulo": valoraciones_por_titulo,
        "valoraciones_inactivas": inactivas,
        "usuarios_dict": usuarios_dict,
        "titulos_dict": titulos_dict,
        "placeholder_movie_img": '/static/img/placeholder_movie.jpg',
        "placeholder_user_img": '/static/img/user-placeholder.png'
    })

@router.get("/valoraciones/crear", response_class=HTMLResponse)
async def pagina_crear_valoracion(request: Request, session: Session = Depends(get_session)):
    usuarios = session.exec(select(Usuario).where(Usuario.is_active == True)).all()
    titulos = session.exec(select(PeliculaSerie).where(PeliculaSerie.is_active == True)).all()
    return templates.TemplateResponse("valoracion_form.html", {
        "request": request, "accion": "Crear", "valoracion": None, "usuarios": usuarios, "titulos": titulos
    })


@router.post("/valoraciones/crear")
async def crear_valoracion_web(id_usuario_FK: int = Form(...), id_titulo_FK: int = Form(...),
                               puntuacion: float = Form(...), comentario: str = Form(...), fecha: str = Form(...),
                               session: Session = Depends(get_session)):
    fecha_obj = datetime.strptime(fecha, "%Y-%m-%d").date()
    nueva_val = Valoracion(id_usuario_FK=id_usuario_FK, id_titulo_FK=id_titulo_FK, puntuacion=puntuacion,
                           comentario=comentario, fecha=fecha_obj)
    session.add(nueva_val)
    session.commit()
    return RedirectResponse(url="/web/valoraciones?mensaje=Valoración registrada", status_code=303)


@router.get("/valoraciones/editar/{id_valoracion}", response_class=HTMLResponse)
async def pagina_editar_valoracion(id_valoracion: int, request: Request, session: Session = Depends(get_session)):
    valoracion = session.get(Valoracion, id_valoracion)
    usuarios = session.exec(select(Usuario).where(Usuario.is_active == True)).all()
    titulos = session.exec(select(PeliculaSerie).where(PeliculaSerie.is_active == True)).all()
    return templates.TemplateResponse("valoracion_form.html",
                                      {"request": request, "accion": "Editar", "valoracion": valoracion,
                                       "usuarios": usuarios, "titulos": titulos})


@router.post("/valoraciones/editar/{id_valoracion}")
async def editar_valoracion_web(id_valoracion: int, id_usuario_FK: int = Form(...), id_titulo_FK: int = Form(...),
                                puntuacion: float = Form(...), comentario: str = Form(...), fecha: str = Form(...),
                                session: Session = Depends(get_session)):
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
# GESTIÓN DE RUTINAS (PLANEADOR SEMANAL)
# ==========================================

@router.get("/rutinas", response_class=HTMLResponse)
async def pagina_rutinas(request: Request, session: Session = Depends(get_session)):
    # 1. Obtener todas las rutinas activas
    rutinas = session.exec(select(Rutina).where(Rutina.is_active == True)).all()

    # =========================================================================
    # CORRECCIÓN AQUÍ: Rellenar todos los días del rango
    # =========================================================================
    rutinas_map = {}

    for r in rutinas:
        fecha_cursor = r.fecha_inicio
        fecha_fin = r.fecha_fin

        # Bucle: Mientras la fecha actual sea menor o igual a la fecha fin
        while fecha_cursor <= fecha_fin:
            fecha_str = fecha_cursor.strftime("%Y-%m-%d")

            # Si la clave no existe, crear la lista para ese día
            if fecha_str not in rutinas_map:
                rutinas_map[fecha_str] = []

            # Agregar la rutina a ese día
            rutinas_map[fecha_str].append(r)

            # Avanzar al siguiente día
            fecha_cursor += timedelta(days=1)
    # =========================================================================

    # 3. Diccionarios para nombres
    usuarios = session.exec(select(Usuario)).all()
    titulos = session.exec(select(PeliculaSerie)).all()
    usuarios_dict = {u.id_usuario: u for u in usuarios}
    titulos_dict = {t.id_titulo: t for t in titulos}

    # 4. Generar Calendario del Mes Actual
    # NOTA: Aquí podrías capturar query params ?year=2023&month=12 para navegar
    # Pero lo dejaremos como lo tienes (mes actual) para no romper nada más.
    hoy = date.today()

    # Variables de navegación básicas para que no falle el template
    # (El template espera prev_year, next_year, etc. según el HTML que enviaste antes)
    year = hoy.year
    month = hoy.month

    cal = calendar.monthcalendar(year, month)

    meses = ["", "Enero", "Febrero", "Marzo", "Abril", "Mayo", "Junio", "Julio", "Agosto", "Septiembre", "Octubre",
             "Noviembre", "Diciembre"]
    nombre_mes = f"{meses[month]} De {year}"

    # Calculamos mes previo y siguiente para los botones
    prev_month = month - 1 if month > 1 else 12
    prev_year = year if month > 1 else year - 1
    next_month = month + 1 if month < 12 else 1
    next_year = year if month < 12 else year + 1

    return templates.TemplateResponse("rutinas.html", {
        "request": request,
        "calendar_weeks": cal,
        "rutinas_map": rutinas_map,  # Ahora lleva los rangos completos
        "usuarios_dict": usuarios_dict,
        "titulos_dict": titulos_dict,
        "year": year,
        "month": month,
        "nombre_mes": nombre_mes,
        "hoy_dia": hoy.day,
        # Agregamos estas variables que tu HTML anterior pedía en los botones < >
        "prev_year": prev_year,
        "prev_month": prev_month,
        "next_year": next_year,
        "next_month": next_month
    })


@router.get("/rutinas/crear", response_class=HTMLResponse)
async def pagina_crear_rutina(request: Request, fecha_preseleccionada: Optional[str] = None,
                              session: Session = Depends(get_session)):
    usuarios = session.exec(select(Usuario).where(Usuario.is_active == True)).all()
    titulos = session.exec(select(PeliculaSerie).where(PeliculaSerie.is_active == True)).all()

    return templates.TemplateResponse("rutina_form.html", {
        "request": request,
        "accion": "Crear",
        "rutina": None,
        "usuarios": usuarios,
        "titulos": titulos,
        "fecha_pre": fecha_preseleccionada  # Pasamos la fecha si viene del calendario
    })


@router.post("/rutinas/crear")
async def crear_rutina_web(nombre: str = Form(...), id_usuario_FK: int = Form(...), id_titulo_FK: int = Form(...),
                           fecha_inicio: str = Form(...), fecha_fin: str = Form(...),
                           session: Session = Depends(get_session)):
    rutina = Rutina(nombre=nombre, id_usuario_FK=id_usuario_FK, id_titulo_FK=id_titulo_FK,
                    fecha_inicio=datetime.strptime(fecha_inicio, "%Y-%m-%d").date(),
                    fecha_fin=datetime.strptime(fecha_fin, "%Y-%m-%d").date())
    session.add(rutina)
    session.commit()
    return RedirectResponse(url="/web/rutinas?mensaje=Rutina creada", status_code=303)


@router.get("/rutinas/editar/{id_rutina}", response_class=HTMLResponse)
async def pagina_editar_rutina(id_rutina: int, request: Request, session: Session = Depends(get_session)):
    rutina = session.get(Rutina, id_rutina)
    usuarios = session.exec(select(Usuario).where(Usuario.is_active == True)).all()
    titulos = session.exec(select(PeliculaSerie).where(PeliculaSerie.is_active == True)).all()
    return templates.TemplateResponse("rutina_form.html",
                                      {"request": request, "accion": "Editar", "rutina": rutina, "usuarios": usuarios,
                                       "titulos": titulos})


@router.post("/rutinas/editar/{id_rutina}")
async def editar_rutina_web(id_rutina: int, nombre: str = Form(...), id_usuario_FK: int = Form(...),
                            id_titulo_FK: int = Form(...), fecha_inicio: str = Form(...), fecha_fin: str = Form(...),
                            session: Session = Depends(get_session)):
    rutina = session.get(Rutina, id_rutina)
    rutina.nombre = nombre
    rutina.id_usuario_FK = id_usuario_FK
    rutina.id_titulo_FK = id_titulo_FK
    rutina.fecha_inicio = datetime.strptime(fecha_inicio, "%Y-%m-%d").date()
    rutina.fecha_fin = datetime.strptime(fecha_fin, "%Y-%m-%d").date()
    session.commit()
    return RedirectResponse(url="/web/rutinas?mensaje=Rutina actualizada", status_code=303)


@router.get("/rutinas/eliminar/{id_rutina}")
async def eliminar_rutina_web(id_rutina: int, session: Session = Depends(get_session)):
    rutina = session.get(Rutina, id_rutina)
    if rutina:
        rutina.is_active = False
        rutina.deleted_at = datetime.now()
        session.commit()
    return RedirectResponse(url="/web/rutinas?mensaje=Rutina eliminada", status_code=303)


# ==========================================
# NUEVO: ESTADÍSTICAS
# ==========================================

@router.get("/estadisticas", response_class=HTMLResponse)
async def pagina_estadisticas(request: Request, session: Session = Depends(get_session)):
    # 1. Conteo General
    n_usuarios = session.exec(select(func.count(Usuario.id_usuario)).where(Usuario.is_active == True)).one()
    n_titulos = session.exec(select(func.count(PeliculaSerie.id_titulo)).where(PeliculaSerie.is_active == True)).one()
    n_valoraciones = session.exec(
        select(func.count(Valoracion.id_valoracion)).where(Valoracion.is_active == True)).one()

    # 2. Películas mejor valoradas (Top Rated)
    # Hacemos un Join para obtener el título y el promedio de sus valoraciones
    top_rated_query = (
        select(PeliculaSerie.titulo, func.avg(Valoracion.puntuacion).label("promedio"))
        .join(Valoracion)
        .where(PeliculaSerie.is_active == True)
        .group_by(PeliculaSerie.id_titulo)
        .order_by(desc("promedio"))
        .limit(5)
    )
    top_rated_results = session.exec(top_rated_query).all()

    # Formatear para Chart.js
    top_rated_labels = [r[0] for r in top_rated_results]
    top_rated_data = [round(r[1], 1) for r in top_rated_results]

    # 3. Distribución por Género
    genre_query = (
        select(PeliculaSerie.genero, func.count(PeliculaSerie.id_titulo))
        .where(PeliculaSerie.is_active == True)
        .group_by(PeliculaSerie.genero)
    )
    genre_results = session.exec(genre_query).all()

    genre_labels = [r[0] for r in genre_results]
    genre_data = [r[1] for r in genre_results]

    return templates.TemplateResponse("estadisticas.html", {
        "request": request,
        "n_usuarios": n_usuarios,
        "n_titulos": n_titulos,
        "n_valoraciones": n_valoraciones,
        "top_rated_labels": top_rated_labels,
        "top_rated_data": top_rated_data,
        "genre_labels": genre_labels,
        "genre_data": genre_data
    })