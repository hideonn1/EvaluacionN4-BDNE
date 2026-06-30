from views.vista_base import VistaBase


class VistaProducto(VistaBase):
    def menu(self) -> str:
        self.mostrar_titulo("GESTIÓN DE PRODUCTOS")
        return self.pedir_opcion(
            {
                "1": "Registrar producto",
                "2": "Listar productos en stock",
                "3": "Eliminar producto",
                "0": "Volver",
            }
        )

    def solicitar_datos_producto(self) -> dict:
        return {
            "nombre": self.pedir_texto("Nombre del producto"),
            "precio": self.pedir_numero("Precio", tipo=float),
            "stock": int(self.pedir_numero("Stock inicial", tipo=int)),
            "categoria": self.pedir_texto("Categoría (opcional)") or None,
        }

    def solicitar_id(self) -> str:
        return self.pedir_texto("ID del producto (_id de Mongo)")

    def mostrar_lista_productos(self, productos: list) -> None:
        if not productos:
            self.mostrar_mensaje("No hay productos disponibles.")
            return
        for p in productos:
            print(
                f"  - [{p.get('_id')}] {p.get('nombre')} "
                f"| stock: {p.get('stock')} | ${p.get('precio')}"
            )
