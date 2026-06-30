class VistaBase:
    @staticmethod
    def mostrar_mensaje(mensaje: str) -> None:
        print(f"[+] {mensaje}")

    @staticmethod
    def mostrar_error(mensaje: str) -> None:
        print(f"[-] {mensaje}")

    @staticmethod
    def mostrar_titulo(titulo: str) -> None:
        print("\n" + "=" * 50)
        print(titulo.center(50))
        print("=" * 50)

    @staticmethod
    def pedir_texto(etiqueta: str) -> str:
        return input(f"{etiqueta}: ").strip()

    @staticmethod
    def pedir_numero(etiqueta: str, tipo=float):
        """Solicita un número (float o int) reintentando hasta recibir uno válido."""
        while True:
            valor = input(f"{etiqueta}: ").strip()
            try:
                return tipo(valor)
            except ValueError:
                VistaBase.mostrar_error("Debe ingresar un número válido.")

    @staticmethod
    def pedir_opcion(opciones: dict) -> str:
        for clave, descripcion in opciones.items():
            print(f"  {clave}) {descripcion}")
        return input("Seleccione una opción: ").strip()
