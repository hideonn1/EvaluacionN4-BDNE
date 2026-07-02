# Punto de entrada de la aplicación SISTEMA COMERCIOTECH.

# Arma la conexión a la base de datos y delega el control de la
# aplicación al ControladorPrincipal (patrón MVC). Mantiene el modo
# '--test-mode', usado por el pipeline de CI/CD para validar que la
# conexión a MongoDB y las consultas básicas funcionan correctamente
# (ver docker-compose.yml / Dockerfile).

import getpass
import sys

import database
from controllers.controlador_principal import ControladorPrincipal
from database import obtener_conexion_db
from models.producto import RepositorioProductos


def solicitar_login(intentos: int = 3) -> str:
    print("\n" + "=" * 50)
    print("SISTEMA COMERCIOTECH - INICIO DE SESIÓN".center(50))
    print("=" * 50)
    for _ in range(intentos):
        usuario = input("Usuario: ").strip()
        password = getpass.getpass("Contraseña: ")
        rol = database.autenticar(usuario, password)
        if rol:
            print(f"[+] Autenticado como: {database.ROLES[rol]['nombre']}")
            return rol
        print("[-] Usuario o contraseña incorrectos.\n")
    print("Demasiados intentos fallidos, cerrando app CLI.", file=sys.stderr)
    sys.exit(1)


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
    rol = solicitar_login()
    db = obtener_conexion_db(rol)
    if db is None:
        print(
            "No se pudo establecer conexión con la base de datos. Revisar archivo .env y que MongoDB esté disponible.",
            file=sys.stderr,
        )
        sys.exit(1)
    app = ControladorPrincipal(db, rol)
    app.ejecutar()


if __name__ == "__main__":
    if "--test-mode" in sys.argv:
        sys.exit(0 if verificar_flujo_ci() else 1)
    else:
        try:
            main()
        except KeyboardInterrupt:
            print("\nSaliendo del sistema...", file=sys.stderr)
            sys.exit(0)
