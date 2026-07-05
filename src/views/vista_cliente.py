from views.vista_base import VistaBase


class VistaCliente(VistaBase):
    def menu(self) -> str:
        self.mostrar_titulo("GESTIÓN DE CLIENTES")
        return self.pedir_opcion(
            {
                "1": "Registrar cliente",
                "2": "Buscar cliente por RUT",
                "3": "Listar clientes",
                "4": "Eliminar cliente",
                "0": "Volver",
            }
        )

    def solicitar_datos_cliente(self) -> dict:
        return {
            "rut": self.pedir_texto("RUT (ej: 12345678-9)"),
            "nombre": self.pedir_texto("Nombre completo"),
            "email": self.pedir_texto("Email"),
            "telefono": self.pedir_texto("Teléfono (opcional)") or None,
            "direccion": self.pedir_texto("Dirección (opcional)") or None,
        }

    def solicitar_rut(self) -> str:
        return self.pedir_texto("RUT del cliente")

    def mostrar_cliente(self, cliente: dict) -> None:
        if not cliente:
            self.mostrar_error("Cliente no encontrado.")
            return
        print(f"  RUT: {cliente.get('rut')}")
        print(f"  Nombre: {cliente.get('nombre')}")
        print(f"  Email: {cliente.get('email')}")
        print(f"  Teléfono: {cliente.get('telefono') or '-'}")
        print(f"  Dirección: {cliente.get('direccion') or '-'}")

    def mostrar_lista_clientes(self, clientes: list) -> None:
        if not clientes:
            self.mostrar_mensaje("No hay clientes registrados.")
            return
        for c in clientes:
            print(f"  - {c.get('rut')} | {c.get('nombre')} | {c.get('email')}")

    def solicitar_datos_modificacion(self, cliente_actual: dict) -> dict:
        print("\n  (Presione Enter para mantener el valor actual)")
        campos = {}

        nuevo_nombre = self.pedir_texto(
            f"Nombre completo [{cliente_actual.get('nombre')}]"
        )
        if nuevo_nombre:
            campos["nombre"] = nuevo_nombre

        nuevo_email = self.pedir_texto(f"Email [{cliente_actual.get('email')}]")
        if nuevo_email:
            campos["email"] = nuevo_email

        nuevo_telefono = input(
            f"Teléfono [{cliente_actual.get('telefono') or '-'}]: "
        ).strip()
        if nuevo_telefono:
            campos["telefono"] = nuevo_telefono

        nueva_direccion = input(
            f"Dirección [{cliente_actual.get('direccion') or '-'}]: "
        ).strip()
        if nueva_direccion:
            campos["direccion"] = nueva_direccion

        return campos
