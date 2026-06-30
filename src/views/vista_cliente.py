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
