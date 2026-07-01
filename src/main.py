# Punto de entrada de la aplicación SISTEMA COMERCIOTECH.

# Arma la conexión a la base de datos y delega el control de la
# aplicación al ControladorPrincipal (patrón MVC). Mantiene el modo
# '--test-mode', usado por el pipeline de CI/CD para validar que la
# conexión a MongoDB y las consultas básicas funcionan correctamente
# (ver docker-compose.yml / Dockerfile).

import sys

from controllers.controlador_principal import ControladorPrincipal
from database import obtener_conexion_db
from models.producto import RepositorioProductos


def verificar_flujo_ci() -> bool:
    # test usado por el pipeline de CI/CD para validar la conexión a datos.
    print("Ejecutando Smoke-Test de conexiones para el Pipeline de Seguridad...")
    try:
        db = obtener_conexion_db()
        if db is None:
            print(
                "Error de integración asíncrona: no se pudo establecer la conexión a la base de datos.",
                file=sys.stderr,
            )
            return False
        repositorio = RepositorioProductos(db)
        productos = repositorio.listar_disponibles()
        print(
            f"Componentes de software enlazados de manera exitosa. "
            f"Elementos leídos: {len(productos)}"
        )
        return True
    except Exception as e:
        print(f"Error de integración asíncrona: {e}", file=sys.stderr)
        return False


def main() -> None:
    print("SISTEMA COMERCIOTECH INICIADO (ENTORNO LOCAL)")
    db = obtener_conexion_db()
    if db is None:
        print(
            "No se pudo establecer conexión con la base de datos. Revisar archivo .env y que MongoDB esté disponible.",
            file=sys.stderr,
        )
        sys.exit(1)
    app = ControladorPrincipal(db)
    app.ejecutar()


if __name__ == "__main__":
    if "--test-mode" in sys.argv:
        sys.exit(0 if verificar_flujo_ci() else 1)
    else:
        main()
