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
async def pagina_rutinas(
        request: Request,
        id_usuario_FK: Optional[int] = None,
        year: Optional[int] = None,
        month: Optional[int] = None,
        session: Session = Depends(get_session)
):
    # 1. Obtener todos los usuarios activos para el selector
    usuarios = session.exec(select(Usuario).where(Usuario.is_active == True)).all()

    hoy = date.today()

    # Base context para la plantilla
    context = {
        "request": request,
        "usuarios": usuarios,
        "selected_user_id": id_usuario_FK,
        "now": hoy,  # Fecha actual para resaltado de día
        "year": year if year is not None else hoy.year,
        "month": month if month is not None else hoy.month
    }

    # Si no se selecciona un usuario, se detiene aquí y se devuelve solo el selector.
    if id_usuario_FK is None:
        return templates.TemplateResponse("rutinas.html", context)

    # --- Usuario seleccionado: Procede con la lógica del calendario ---

    # 2. Filtrar rutinas por usuario seleccionado
    query = select(Rutina).where(Rutina.is_active == True, Rutina.id_usuario_FK == id_usuario_FK)
    rutinas = session.exec(query).all()

    # 3. Mapeo de rutinas por día
    rutinas_map = {}
    for r in rutinas:
        fecha_cursor = r.fecha_inicio
        fecha_fin = r.fecha_fin

        while fecha_cursor <= fecha_fin:
            fecha_str = fecha_cursor.strftime("%Y-%m-%d")

            if fecha_str not in rutinas_map:
                rutinas_map[fecha_str] = []

            rutinas_map[fecha_str].append(r)
            fecha_cursor += timedelta(days=1)

    # 4. Diccionario de Títulos (para mostrar el nombre del título en el calendario)
    titulos = session.exec(select(PeliculaSerie).where(PeliculaSerie.is_active == True)).all()
    titulos_dict = {t.id_titulo: t for t in titulos}

    # 5. Generación del Calendario (usa fecha actual o parámetros de URL)
    target_year = year if year is not None else hoy.year
    target_month = month if month is not None else hoy.month

    try:
        target_date = date(target_year, target_month, 1)
    except ValueError:
        target_date = date(hoy.year, hoy.month, 1)

    year = target_date.year
    month = target_date.month

    cal = calendar.monthcalendar(year, month)

    meses = ["", "Enero", "Febrero", "Marzo", "Abril", "Mayo", "Junio", "Julio", "Agosto", "Septiembre", "Octubre",
             "Noviembre", "Diciembre"]
    nombre_mes = f"{meses[month]} De {year}"

    # Calcular mes previo y siguiente (navegación)
    prev_date = target_date - timedelta(days=1)
    prev_month = prev_date.month
    prev_year = prev_date.year

    if month == 12:
        next_month = 1
        next_year = year + 1
    else:
        next_month = month + 1
        next_year = year

    context.update({
        "calendar_weeks": cal,
        "rutinas_map": rutinas_map,
        "titulos_dict": titulos_dict,
        "year": year,
        "month": month,
        "nombre_mes": nombre_mes,
        "hoy_dia": hoy.day,
        "prev_year": prev_year,
        "prev_month": prev_month,
        "next_year": next_year,
        "next_month": next_month
    })

    return templates.TemplateResponse("rutinas.html", context)


@router.get("/rutinas/crear", response_class=HTMLResponse)
async def pagina_crear_rutina(
        request: Request,
        fecha_preseleccionada: Optional[str] = None,
        id_usuario_FK: Optional[int] = None,  # Para pre-seleccionar desde el calendario
        session: Session = Depends(get_session)
):
    usuarios = session.exec(select(Usuario).where(Usuario.is_active == True)).all()
    titulos = session.exec(select(PeliculaSerie).where(PeliculaSerie.is_active == True)).all()

    return templates.TemplateResponse("rutina_form.html", {
        "request": request,
        "accion": "Crear",
        "rutina": None,
        "usuarios": usuarios,
        "titulos": titulos,
        "fecha_pre": fecha_preseleccionada,
        "selected_user_id": id_usuario_FK
    })


@router.post("/rutinas/crear")
async def crear_rutina_web(
        nombre: str = Form(...),
        id_usuario_FK: int = Form(...),
        id_titulo_FK: int = Form(...),
        fecha_inicio: str = Form(...),
        fecha_fin: str = Form(...),
        session: Session = Depends(get_session)):
    # 1. Conversión y Validación de Fechas
    try:
        f_inicio = datetime.strptime(fecha_inicio, "%Y-%m-%d").date()
        f_fin = datetime.strptime(fecha_fin, "%Y-%m-%d").date()
    except ValueError:
        raise HTTPException(status_code=400, detail="Formato de fecha inválido. Use AAAA-MM-DD.")

    if f_inicio > f_fin:
        raise HTTPException(status_code=400, detail="La fecha de inicio no puede ser posterior a la fecha de fin.")

    # 2. Validación de Claves Foráneas (Usuario y Título deben existir y estar activos)
    usuario = session.get(Usuario, id_usuario_FK)
    titulo = session.get(PeliculaSerie, id_titulo_FK)

    if not usuario or not usuario.is_active:
        raise HTTPException(status_code=404, detail=f"Usuario con ID {id_usuario_FK} no encontrado o inactivo")
    if not titulo or not titulo.is_active:
        raise HTTPException(status_code=404, detail=f"Título con ID {id_titulo_FK} no encontrado o inactivo")

    # 3. Creación
    rutina = Rutina(nombre=nombre, id_usuario_FK=id_usuario_FK, id_titulo_FK=id_titulo_FK,
                    fecha_inicio=f_inicio, fecha_fin=f_fin)
    session.add(rutina)
    session.commit()

    # Redirección de vuelta al calendario del usuario seleccionado
    return RedirectResponse(
        url=f"/web/rutinas?id_usuario_FK={id_usuario_FK}&mensaje=Rutina creada",
        status_code=303
    )


@router.get("/rutinas/editar/{id_rutina}", response_class=HTMLResponse)
async def pagina_editar_rutina(id_rutina: int, request: Request, session: Session = Depends(get_session)):
    rutina = session.get(Rutina, id_rutina)
    usuarios = session.exec(select(Usuario).where(Usuario.is_active == True)).all()
    titulos = session.exec(select(PeliculaSerie).where(PeliculaSerie.is_active == True)).all()

    if not rutina:
        raise HTTPException(status_code=404, detail=f"Rutina con ID {id_rutina} no encontrada")

    return templates.TemplateResponse("rutina_form.html",
                                      {"request": request, "accion": "Editar", "rutina": rutina, "usuarios": usuarios,
                                       "titulos": titulos, "selected_user_id": rutina.id_usuario_FK})


@router.post("/rutinas/editar/{id_rutina}")
async def editar_rutina_web(
        id_rutina: int,
        nombre: str = Form(...),
        id_usuario_FK: int = Form(...),  # Valor del campo oculto
        id_titulo_FK: int = Form(...),  # Valor del campo oculto
        fecha_inicio: str = Form(...),
        fecha_fin: str = Form(...),
        session: Session = Depends(get_session)):
    rutina = session.get(Rutina, id_rutina)
    if not rutina:
        raise HTTPException(status_code=404, detail=f"Rutina con ID {id_rutina} no encontrada")

    # 1. Conversión y Validación de Fechas
    try:
        f_inicio = datetime.strptime(fecha_inicio, "%Y-%m-%d").date()
        f_fin = datetime.strptime(fecha_fin, "%Y-%m-%d").date()
    except ValueError:
        raise HTTPException(status_code=400, detail="Formato de fecha inválido. Use AAAA-MM-DD.")

    if f_inicio > f_fin:
        raise HTTPException(status_code=400, detail="La fecha de inicio no puede ser posterior a la fecha de fin.")

    # 2. Actualización de datos
    rutina.nombre = nombre
    rutina.id_usuario_FK = id_usuario_FK
    rutina.id_titulo_FK = id_titulo_FK
    rutina.fecha_inicio = f_inicio
    rutina.fecha_fin = f_fin

    session.commit()

    # Redirección de vuelta al calendario del usuario seleccionado
    return RedirectResponse(
        url=f"/web/rutinas?id_usuario_FK={id_usuario_FK}&mensaje=Rutina actualizada",
        status_code=303
    )


@router.get("/rutinas/eliminar/{id_rutina}")
async def eliminar_rutina_web(id_rutina: int, session: Session = Depends(get_session)):
    rutina = session.get(Rutina, id_rutina)
    user_id = None
    if rutina:
        user_id = rutina.id_usuario_FK  # Obtener ID para la redirección
        rutina.is_active = False
        rutina.deleted_at = datetime.now()
        session.commit()

    # Redirección de vuelta al calendario del usuario (si se pudo obtener el ID)
    url = f"/web/rutinas?id_usuario_FK={user_id}&mensaje=Rutina eliminada" if user_id else "/web/rutinas?mensaje=Rutina eliminada"
    return RedirectResponse(url=url, status_code=303)


# ==========================================
# NUEVO: ESTADÍSTICAS
# ==========================================

@router.get("/estadisticas", response_class=HTMLResponse)
async def pagina_estadisticas(request: Request, session: Session = Depends(get_session)):
    # 1. Conteo General y Promedio Global (Nuevos KPIs)
    n_usuarios = session.exec(select(func.count(Usuario.id_usuario)).where(Usuario.is_active == True)).one()
    n_titulos = session.exec(select(func.count(PeliculaSerie.id_titulo)).where(PeliculaSerie.is_active == True)).one()
    n_valoraciones = session.exec(
        select(func.count(Valoracion.id_valoracion)).where(Valoracion.is_active == True)).one()

    # NUEVO KPI: Total Rutinas
    n_rutinas = session.exec(select(func.count(Rutina.id_rutina)).where(Rutina.is_active == True)).one()

    # NUEVO KPI: Promedio Global
    promedio_global_query = select(func.avg(Valoracion.puntuacion)).where(Valoracion.is_active == True)
    promedio_global_raw = session.exec(promedio_global_query).one_or_none()
    promedio_global = round(promedio_global_raw, 1) if promedio_global_raw is not None else 0.0

    # 2. Películas mejor valoradas (Top Rated) - Se mantiene
    top_rated_query = (
        select(PeliculaSerie.titulo, func.avg(Valoracion.puntuacion).label("promedio"))
        .join(Valoracion)
        .where(PeliculaSerie.is_active == True, Valoracion.is_active == True)
        .group_by(PeliculaSerie.id_titulo)
        .order_by(desc("promedio"))
        .limit(5)
    )
    top_rated_results = session.exec(top_rated_query).all()
    top_rated_labels = [r[0] for r in top_rated_results]
    top_rated_data = [round(r[1], 1) for r in top_rated_results]

    # 3. Distribución por Género (Título Count) - Se mantiene (ordenado por conteo)
    genre_query = (
        select(PeliculaSerie.genero, func.count(PeliculaSerie.id_titulo))
        .where(PeliculaSerie.is_active == True)
        .group_by(PeliculaSerie.genero)
        .order_by(desc(func.count(PeliculaSerie.id_titulo)))
    )
    genre_results = session.exec(genre_query).all()
    genre_labels = [r[0] for r in genre_results]
    genre_data = [r[1] for r in genre_results]

    # NUEVA ESTADÍSTICA: Top 5 Géneros más valorados (por número de reseñas)
    most_rated_genres_query = (
        select(PeliculaSerie.genero, func.count(Valoracion.id_valoracion).label("total_reviews"))
        .join(Valoracion, PeliculaSerie.id_titulo == Valoracion.id_titulo_FK)
        .where(PeliculaSerie.is_active == True, Valoracion.is_active == True)
        .group_by(PeliculaSerie.genero)
        .order_by(desc("total_reviews"))
        .limit(5)
    )
    most_rated_genres_results = session.exec(most_rated_genres_query).all()
    most_rated_genres_labels = [r[0] for r in most_rated_genres_results]
    most_rated_genres_data = [r[1] for r in most_rated_genres_results]

    # NUEVA ESTADÍSTICA: Títulos por Año de Estreno (Top 5)
    titles_by_year_query = (
        select(PeliculaSerie.anio_estreno, func.count(PeliculaSerie.id_titulo).label("total_titles"))
        .where(PeliculaSerie.is_active == True)
        .group_by(PeliculaSerie.anio_estreno)
        .order_by(desc("total_titles"))
        .limit(5)
    )
    titles_by_year_results = session.exec(titles_by_year_query).all()
    titles_by_year_labels = [str(r[0]) for r in titles_by_year_results]
    titles_by_year_data = [r[1] for r in titles_by_year_results]

    return templates.TemplateResponse("estadisticas.html", {
        "request": request,
        # KPIs
        "n_usuarios": n_usuarios,
        "n_titulos": n_titulos,
        "n_valoraciones": n_valoraciones,
        "n_rutinas": n_rutinas,
        "promedio_global": promedio_global,
        # Gráficos existentes
        "top_rated_labels": top_rated_labels,
        "top_rated_data": top_rated_data,
        "genre_labels": genre_labels,
        "genre_data": genre_data,
        # Gráficos nuevos
        "most_rated_genres_labels": most_rated_genres_labels,
        "most_rated_genres_data": most_rated_genres_data,
        "titles_by_year_labels": titles_by_year_labels,
        "titles_by_year_data": titles_by_year_data,
    })