from sqlmodel import SQLModel, Field, Relationship
from typing import Optional, List
from datetime import date

class Usuario(SQLModel, table=True):
    id_usuario: Optional[int] = Field(default=None, primary_key=True)
    nombre: str
    correo: str = Field(unique=True, index=True)
    clave: str

    # Relaciones: un usuario puede tener muchas valoraciones y rutinas
    valoraciones: List["Valoracion"] = Relationship(back_populates="usuario")
    rutinas: List["Rutina"] = Relationship(back_populates="usuario")



class PeliculaSerie(SQLModel, table=True):
    id_titulo: Optional[int] = Field(default=None, primary_key=True)
    titulo: str
    genero: str
    anio_estreno: int
    duracion: int
    descripcion: str

    # Relaciones: un título puede tener muchas valoraciones y rutinas
    valoraciones: List["Valoracion"] = Relationship(back_populates="titulo")
    rutinas: List["Rutina"] = Relationship(back_populates="titulo")



class Valoracion(SQLModel, table=True):
    id_valoracion: Optional[int] = Field(default=None, primary_key=True)
    puntuacion: float
    comentario: str
    fecha: date

    # Llaves foráneas
    id_usuario_FK: int = Field(foreign_key="usuario.id_usuario")
    id_titulo_FK: int = Field(foreign_key="peliculaserie.id_titulo")

    # Relaciones inversas
    usuario: Optional[Usuario] = Relationship(back_populates="valoraciones")
    titulo: Optional[PeliculaSerie] = Relationship(back_populates="valoraciones")



class Rutina(SQLModel, table=True):
    id_rutina: Optional[int] = Field(default=None, primary_key=True)
    nombre: str
    fecha_inicio: date
    fecha_fin: date

    # Llaves foráneas
    id_usuario_FK: int = Field(foreign_key="usuario.id_usuario")
    id_titulo_FK: int = Field(foreign_key="peliculaserie.id_titulo")

    # Relaciones inversas
    usuario: Optional[Usuario] = Relationship(back_populates="rutinas")
    titulo: Optional[PeliculaSerie] = Relationship(back_populates="rutinas")
