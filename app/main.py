from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse
from strawberry.fastapi import GraphQLRouter
import time

from .core.config import settings
from .core.database import engine
from .models import Base
from .exceptions import setup_exception_handlers
from .graphql import schema
# Solo mantener auth si quieres autenticación REST opcional
from .routers import auth

# Inicialización de la base de datos
Base.metadata.create_all(bind=engine)

app = FastAPI(
    title=f"{settings.PROJECT_NAME} - GraphQL API",
    version="2.0.0",
    description="API GraphQL para gestión de registros",
    docs_url="/docs",
    redoc_url="/redoc",
)

# Configuración de CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=[str(origin) for origin in settings.BACKEND_CORS_ORIGINS],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Middleware para logging
@app.middleware("http")
async def add_process_time_header(request: Request, call_next):
    start_time = time.time()
    response = await call_next(request)
    process_time = time.time() - start_time
    response.headers["X-Process-Time"] = str(process_time)
    return response

# Configurar manejadores de excepciones
setup_exception_handlers(app, debug=settings.DEBUG)

# Router GraphQL principal
graphql_app = GraphQLRouter(schema, graphiql=True)
app.include_router(graphql_app, prefix="/graphql")

# Opcional: mantener autenticación REST
app.include_router(auth.router)

# Página de bienvenida (como la mostré antes)
@app.get("/", response_class=HTMLResponse)
async def root():
    html_content = """
    <!DOCTYPE html>
    <html>
        <head>
            <title>API GraphQL con SQL Server</title>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <style>
                body {
                    font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
                    margin: 0;
                    padding: 0;
                    display: flex;
                    justify-content: center;
                    align-items: center;
                    min-height: 100vh;
                    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                }
                .container {
                    background-color: white;
                    border-radius: 12px;
                    box-shadow: 0 8px 30px rgba(0, 0, 0, 0.12);
                    padding: 2.5rem;
                    max-width: 800px;
                    width: 90%;
                }
                h1 {
                    color: #2c3e50;
                    margin-bottom: 1.5rem;
                    font-size: 2.2rem;
                    border-bottom: 2px solid #eaeaea;
                    padding-bottom: 0.8rem;
                }
                p {
                    color: #555;
                    line-height: 1.7;
                    font-size: 1.1rem;
                    margin-bottom: 1.5rem;
                }
                .features {
                    background-color: #f8f9fa;
                    border-radius: 8px;
                    padding: 1.2rem;
                    margin-bottom: 1.5rem;
                }
                .features h2 {
                    color: #e91e63;
                    margin-top: 0;
                    font-size: 1.4rem;
                }
                .features ul {
                    padding-left: 1.2rem;
                }
                .features li {
                    margin-bottom: 0.5rem;
                    color: #555;
                }
                .buttons {
                    margin-top: 2rem;
                    display: flex;
                    gap: 1rem;
                    flex-wrap: wrap;
                }
                .button {
                    display: inline-block;
                    background-color: #e91e63;
                    color: white;
                    padding: 0.8rem 1.8rem;
                    text-decoration: none;
                    border-radius: 6px;
                    font-weight: bold;
                    transition: all 0.3s ease;
                    box-shadow: 0 4px 6px rgba(50, 50, 93, 0.11);
                }
                .button:hover {
                    background-color: #c2185b;
                    transform: translateY(-2px);
                }
                .button.secondary {
                    background-color: #673ab7;
                }
                .button.secondary:hover {
                    background-color: #512da8;
                }
                .version {
                    margin-top: 2rem;
                    font-size: 0.9rem;
                    color: #7f8c8d;
                    text-align: center;
                }
            </style>
        </head>
        <body>
            <div class="container">
                <h1>🚀 API GraphQL con SQL Server</h1>
                <p>Bienvenido a la nueva API GraphQL para gestión de registros. Esta API utiliza GraphQL para proporcionar una interfaz flexible y eficiente.</p>

                <div class="features">
                    <h2>Características GraphQL:</h2>
                    <ul>
                        <li>Consultas flexibles - solicita solo los datos que necesitas</li>
                        <li>Mutaciones para crear, actualizar y eliminar registros</li>
                        <li>Esquema fuertemente tipado</li>
                        <li>Interfaz GraphiQL integrada para pruebas</li>
                        <li>Validaciones robustas de datos</li>
                        <li>Manejo de errores descriptivo</li>
                    </ul>
                </div>

                <p>Utiliza GraphiQL para explorar el esquema y probar las consultas disponibles.</p>

                <div class="buttons">
                    <a href="/graphql" class="button">Explorador GraphiQL</a>
                    <a href="/docs" class="button secondary">Documentación FastAPI</a>
                    <a href="/health" class="button secondary">Estado del Sistema</a>
                </div>

                <div class="version">
                    <p>Versión 2.0.0 - API GraphQL | Registros: 3 campos (ID, Documento, Nombre)</p>
                </div>
            </div>
        </body>
    </html>
    """
    return html_content

# Endpoint de salud
@app.get("/health")
async def health_check():
    return {
        "status": "online",
        "version": "2.0.0",
        "api_type": "GraphQL",
        "timestamp": time.time()
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=settings.DEBUG)