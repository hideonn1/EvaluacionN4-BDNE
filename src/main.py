import sys

from crud import listar_productos_en_stock


def verificar_flujo_ci():
    print("Ejecutando Smoke-Test de conexiones para el Pipeline de Seguridad...")
    try:
        productos = listar_productos_en_stock()
        print(
            f"Componentes de software enlazados de manera exitosa. Elementos leídos: {len(productos)}"
        )
        return True
    except Exception as e:
        print(f"Error de integración asíncrona: {e}", file=sys.stderr)
        return False


if __name__ == "__main__":
    if "--test-mode" in sys.argv:
        if verificar_flujo_ci():
            sys.exit(0)
        sys.exit(1)
    else:
        print("SISTEMA COMERCIOTECH INICIADO (ENTORNO LOCAL)")
