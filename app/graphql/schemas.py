import strawberry
from typing import List, Optional
from datetime import datetime

@strawberry.type
class Registro:
    id: int
    documento: int
    nombre: str
    fecha_creacion: datetime

@strawberry.input
class RegistroInput:
    documento: int
    nombre: str

@strawberry.input
class RegistroUpdateInput:
    documento: Optional[int] = None
    nombre: Optional[str] = None

@strawberry.type
class RegistroResponse:
    success: bool
    message: str
    registro: Optional[Registro] = None

@strawberry.type
class RegistroListResponse:
    success: bool
    message: str
    registros: List[Registro]
    total: int