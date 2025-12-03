
from utils.db import engine
from sqlmodel import SQLModel

print("Creando tablas en la base de datos...")

SQLModel.metadata.create_all(engine)

print("Â¡Tablas creadas correctamente!")
