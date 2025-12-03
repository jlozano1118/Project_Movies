from sqlmodel import SQLModel, Field, Relationship
from typing import Optional, List
from datetime import date, datetime


class Usuario(SQLModel, table=True):
    id_usuario: Optional[int] = Field(default=None, primary_key=True, index=True)
    nombre: str
    correo: str = Field(unique=True, index=True)
    clave: str
    is_active: bool = Field(default=True)
    deleted_at: Optional[datetime] = Field(default=None, nullable=True)

    valoraciones: List["Valoracion"] = Relationship(back_populates="usuario")
    rutinas: List["Rutina"] = Relationship(back_populates="usuario")


class PeliculaSerie(SQLModel, table=True):
    id_titulo: Optional[int] = Field(default=None, primary_key=True, index=True)
    titulo: str = Field(unique=True, index=True)
    genero: str
    anio_estreno: int
    duracion: int
    descripcion: str
    is_active: bool = Field(default=True)
    deleted_at: Optional[datetime] = Field(default=None, nullable=True)

    valoraciones: List["Valoracion"] = Relationship(back_populates="titulo")
    rutinas: List["Rutina"] = Relationship(back_populates="titulo")


class Valoracion(SQLModel, table=True):
    id_valoracion: Optional[int] = Field(default=None, primary_key=True, index=True)
    puntuacion: float
    comentario: str
    fecha: date
    is_active: bool = Field(default=True)
    deleted_at: Optional[datetime] = Field(default=None, nullable=True)

    id_usuario_FK: int = Field(foreign_key="usuario.id_usuario")
    id_titulo_FK: int = Field(foreign_key="peliculaserie.id_titulo")

    usuario: Optional["Usuario"] = Relationship(back_populates="valoraciones")
    titulo: Optional["PeliculaSerie"] = Relationship(back_populates="valoraciones")


class Rutina(SQLModel, table=True):
    id_rutina: Optional[int] = Field(default=None, primary_key=True, index=True)
    nombre: str = Field(index=True)
    fecha_inicio: date
    fecha_fin: date
    is_active: bool = Field(default=True)
    deleted_at: Optional[datetime] = Field(default=None, nullable=True)

    id_usuario_FK: int = Field(foreign_key="usuario.id_usuario")
    id_titulo_FK: int = Field(foreign_key="peliculaserie.id_titulo")

    usuario: Optional["Usuario"] = Relationship(back_populates="rutinas")
    titulo: Optional["PeliculaSerie"] = Relationship(back_populates="rutinas")


# Schemas para crear entidades sin ID (para el POST)
class UsuarioCreate(SQLModel):
    nombre: str
    correo: str
    clave: str


class PeliculaSerieCreate(SQLModel):
    titulo: str
    genero: str
    anio_estreno: int
    duracion: int
    descripcion: str


class ValoracionCreate(SQLModel):
    puntuacion: float
    comentario: str
    fecha: date
    id_usuario_FK: int
    id_titulo_FK: int


class RutinaCreate(SQLModel):
    nombre: str
    fecha_inicio: date
    fecha_fin: date
    id_usuario_FK: int
    id_titulo_FK: int