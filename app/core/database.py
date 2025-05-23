from sqlalchemy import create_engine, event
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from sqlalchemy.engine import Engine
from .config import settings

# Crear el motor de base de datos con configuraciones específicas para SQL Server
engine = create_engine(
    settings.SQLALCHEMY_DATABASE_URI,
    pool_pre_ping=True,
    pool_recycle=3600,
    echo=settings.DEBUG,
    # Configuraciones específicas para SQL Server
    connect_args={
        "autocommit": False,
    }
)

# Crear la sesión
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Base para los modelos
Base = declarative_base()

# Función para obtener la sesión de la BD
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# Evento para establecer configuraciones específicas para SQL Server
@event.listens_for(Engine, "connect")
def set_mssql_options(dbapi_connection, connection_record):
    """Configurar opciones específicas de SQL Server"""
    cursor = dbapi_connection.cursor()
    # Estas configuraciones ayudan con el problema de rowcount
    cursor.execute("SET NOCOUNT OFF")  # Cambiar a OFF para obtener el conteo correcto
    cursor.execute("SET IMPLICIT_TRANSACTIONS OFF")
    cursor.close()

# Evento adicional para configurar la sesión
@event.listens_for(SessionLocal, "before_commit")
def receive_before_commit(session):
    """Configuraciones antes del commit"""
    pass