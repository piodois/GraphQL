import strawberry
from typing import List, Optional
from strawberry.types import Info
from sqlalchemy.orm import Session
from ..core.database import get_db
from ..models.registro import Registro as RegistroModel
from ..exceptions import NotFoundException, BadRequestException
from .schemas import (
    Registro, RegistroInput, RegistroUpdateInput,
    RegistroResponse, RegistroListResponse
)


def get_db_session():
    """Obtener sesión de base de datos para GraphQL"""
    return next(get_db())


@strawberry.type
class Query:
    @strawberry.field
    def registros(
            self,
            info: Info,
            skip: int = 0,
            limit: int = 100
    ) -> RegistroListResponse:
        """Obtener lista de registros"""
        db = get_db_session()
        try:
            registros = db.query(RegistroModel).order_by(RegistroModel.id).offset(skip).limit(limit).all()
            total = db.query(RegistroModel).count()

            return RegistroListResponse(
                success=True,
                message="Registros obtenidos exitosamente",
                registros=[
                    Registro(
                        id=r.id,
                        documento=r.documento,
                        nombre=r.nombre,
                        fecha_creacion=r.fecha_creacion
                    ) for r in registros
                ],
                total=total
            )
        except Exception as e:
            return RegistroListResponse(
                success=False,
                message=f"Error al obtener registros: {str(e)}",
                registros=[],
                total=0
            )
        finally:
            db.close()

    @strawberry.field
    def registro(self, info: Info, id: int) -> RegistroResponse:
        """Obtener un registro por ID"""
        db = get_db_session()
        try:
            registro = db.query(RegistroModel).filter(RegistroModel.id == id).first()
            if not registro:
                return RegistroResponse(
                    success=False,
                    message="Registro no encontrado",
                    registro=None
                )

            return RegistroResponse(
                success=True,
                message="Registro encontrado",
                registro=Registro(
                    id=registro.id,
                    documento=registro.documento,
                    nombre=registro.nombre,
                    fecha_creacion=registro.fecha_creacion
                )
            )
        except Exception as e:
            return RegistroResponse(
                success=False,
                message=f"Error al obtener registro: {str(e)}",
                registro=None
            )
        finally:
            db.close()


@strawberry.type
class Mutation:
    @strawberry.field
    def crear_registro(
            self,
            info: Info,
            registro_input: RegistroInput
    ) -> RegistroResponse:
        """Crear un nuevo registro"""
        db = get_db_session()
        try:
            # Validación básica
            if registro_input.documento <= 0:
                return RegistroResponse(
                    success=False,
                    message="El documento debe ser un número positivo",
                    registro=None
                )

            if len(registro_input.nombre) < 2:
                return RegistroResponse(
                    success=False,
                    message="El nombre debe tener al menos 2 caracteres",
                    registro=None
                )

            # Verificar si el documento ya existe
            existe = db.query(RegistroModel).filter(RegistroModel.documento == registro_input.documento).first()
            if existe:
                return RegistroResponse(
                    success=False,
                    message="Ya existe un registro con ese documento",
                    registro=None
                )

            # Crear registro
            nuevo_registro = RegistroModel(
                documento=registro_input.documento,
                nombre=registro_input.nombre
            )

            db.add(nuevo_registro)
            db.commit()
            db.refresh(nuevo_registro)

            return RegistroResponse(
                success=True,
                message="Registro creado exitosamente",
                registro=Registro(
                    id=nuevo_registro.id,
                    documento=nuevo_registro.documento,
                    nombre=nuevo_registro.nombre,
                    fecha_creacion=nuevo_registro.fecha_creacion
                )
            )

        except Exception as e:
            db.rollback()
            return RegistroResponse(
                success=False,
                message=f"Error al crear registro: {str(e)}",
                registro=None
            )
        finally:
            db.close()

    @strawberry.field
    def actualizar_registro(
            self,
            info: Info,
            id: int,
            registro_input: RegistroUpdateInput
    ) -> RegistroResponse:
        """Actualizar un registro existente"""
        db = get_db_session()
        try:
            registro = db.query(RegistroModel).filter(RegistroModel.id == id).first()
            if not registro:
                return RegistroResponse(
                    success=False,
                    message="Registro no encontrado",
                    registro=None
                )

            # Actualizar campos si se proporcionan
            if registro_input.documento is not None:
                if registro_input.documento <= 0:
                    return RegistroResponse(
                        success=False,
                        message="El documento debe ser un número positivo",
                        registro=None
                    )

                # Verificar si el nuevo documento ya existe en otro registro
                existe = db.query(RegistroModel).filter(
                    RegistroModel.documento == registro_input.documento,
                    RegistroModel.id != id
                ).first()
                if existe:
                    return RegistroResponse(
                        success=False,
                        message="Ya existe otro registro con ese documento",
                        registro=None
                    )

                registro.documento = registro_input.documento

            if registro_input.nombre is not None:
                if len(registro_input.nombre) < 2:
                    return RegistroResponse(
                        success=False,
                        message="El nombre debe tener al menos 2 caracteres",
                        registro=None
                    )
                registro.nombre = registro_input.nombre

            db.commit()
            db.refresh(registro)

            return RegistroResponse(
                success=True,
                message="Registro actualizado exitosamente",
                registro=Registro(
                    id=registro.id,
                    documento=registro.documento,
                    nombre=registro.nombre,
                    fecha_creacion=registro.fecha_creacion
                )
            )

        except Exception as e:
            db.rollback()
            return RegistroResponse(
                success=False,
                message=f"Error al actualizar registro: {str(e)}",
                registro=None
            )
        finally:
            db.close()

    @strawberry.field
    def eliminar_registro(
            self,
            info: Info,
            id: int
    ) -> RegistroResponse:
        """Eliminar un registro"""
        db = get_db_session()
        try:
            registro = db.query(RegistroModel).filter(RegistroModel.id == id).first()
            if not registro:
                return RegistroResponse(
                    success=False,
                    message="Registro no encontrado",
                    registro=None
                )

            registro_eliminado = Registro(
                id=registro.id,
                documento=registro.documento,
                nombre=registro.nombre,
                fecha_creacion=registro.fecha_creacion
            )

            db.delete(registro)
            db.commit()

            return RegistroResponse(
                success=True,
                message="Registro eliminado exitosamente",
                registro=registro_eliminado
            )

        except Exception as e:
            db.rollback()
            return RegistroResponse(
                success=False,
                message=f"Error al eliminar registro: {str(e)}",
                registro=None
            )
        finally:
            db.close()