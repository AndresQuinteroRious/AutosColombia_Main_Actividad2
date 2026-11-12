"""Elimina administradores adicionales dejando solo uno."""

import sys

from sqlalchemy import text
from sqlalchemy.exc import SQLAlchemyError

from app.config import ConfigurationError, load_database_settings
from app.database import create_database_engine


def main() -> int:
    engine = None
    try:
        engine = create_database_engine(load_database_settings())
        with engine.connect() as connection:
            # Listar todos los administradores
            result = connection.execute(text("SELECT id, nombre, documento FROM usuario WHERE rol = 'ADMINISTRADOR'"))
            admins = [dict(row._mapping) for row in result]
            
            if len(admins) <= 1:
                print(f"Ya solo hay {len(admins)} administrador(es). No se requiere acción.")
                return 0
            
            print(f"Se encontraron {len(admins)} administradores:")
            for a in admins:
                print(f"  - ID: {a['id']}, Nombre: {a['nombre']}, Documento: {a['documento']}")
            
            # Eliminar todos excepto el primero (el más antiguo)
            to_delete = admins[1:]  # Mantener el primero, eliminar el resto
            print(f"\nEliminando {len(to_delete)} administrador(es) adicional(es)...")
            
            for admin in to_delete:
                connection.execute(text("DELETE FROM usuario WHERE id = :id"), {"id": admin['id']})
                print(f"  - Eliminado: {admin['nombre']} (ID: {admin['id']})")
            
            connection.commit()
            print("\nAdministradores adicionales eliminados exitosamente.")
            return 0
    except ConfigurationError as error:
        print(str(error), file=sys.stderr)
        return 2
    except (SQLAlchemyError, OSError, ValueError) as e:
        print(f"Error: {e}", file=sys.stderr)
        return 1
    finally:
        if engine is not None:
            engine.dispose()


if __name__ == "__main__":
    raise SystemExit(main())
