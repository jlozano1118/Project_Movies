from fastapi import APIRouter, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates

router = APIRouter(
    prefix="/web",
    tags=["Web Interface"]
)

templates = Jinja2Templates(directory="templates")


@router.get("/usuarios", response_class=HTMLResponse)
async def pagina_usuarios(request: Request):
    return templates.TemplateResponse("usuarios.html", {"request": request})


@router.get("/titulos", response_class=HTMLResponse)
async def pagina_titulos(request: Request):
    return templates.TemplateResponse("titulos.html", {"request": request})


@router.get("/valoraciones", response_class=HTMLResponse)
async def pagina_valoraciones(request: Request):
    return templates.TemplateResponse("valoraciones.html", {"request": request})


@router.get("/rutinas", response_class=HTMLResponse)
async def pagina_rutinas(request: Request):
    return templates.TemplateResponse("rutinas.html", {"request": request})