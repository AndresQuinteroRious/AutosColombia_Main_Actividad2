"""Verifica si hay usuarios en la base de datos."""

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
            result = connection.execute(text("SELECT id, nombre, documento, rol FROM usuario"))
            usuarios = [dict(row._mapping) for row in result]
            if not usuarios:
                print("No hay usuarios en la base de datos.")
            else:
                print(f"Total de usuarios: {len(usuarios)}")
                for u in usuarios:
                    print(f"  - ID: {u['id']}, Nombre: {u['nombre']}, Documento: {u['documento']}, Rol: {u['rol']}")
        return 0
    except ConfigurationError as error:
        print(str(error), file=sys.stderr)
        return 2
    except (SQLAlchemyError, OSError, ValueError):
        print("No se pudo conectar a PostgreSQL.", file=sys.stderr)
        return 1
    finally:
        if engine is not None:
            engine.dispose()


if __name__ == "__main__":
    raise SystemExit(main())
