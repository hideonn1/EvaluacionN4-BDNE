from views.vista_base import VistaBase


class VistaPedido(VistaBase):
    def menu(self) -> str:
        self.mostrar_titulo("GESTIÓN DE PEDIDOS")
        return self.pedir_opcion(
            {
                "1": "Listar pedidos activos",
                "2": "Listar todos los pedidos",
                "3": "Cambiar estado de un pedido",
                "4": "Eliminar pedido",
                "0": "Volver",
            }
        )

    def solicitar_codigo(self) -> str:
        return self.pedir_texto("Código del pedido")

    def solicitar_estado(self) -> str:
        return self.pedir_texto(
            "Nuevo estado (pendiente/procesando/enviado/entregado/cancelado)"
        )

    def mostrar_lista_pedidos(self, pedidos: list) -> None:
        if not pedidos:
            self.mostrar_mensaje("No hay pedidos para mostrar.")
            return
        for p in pedidos:
            print(
                f"  - {p.get('codigo_pedido')} | cliente: {p.get('rut_cliente')} "
                f"| estado: {p.get('estado')} | total: ${p.get('total')}"
            )
            for item in p.get("items", []):
                print(
                    f"      · {item.get('cantidad')}x {item.get('nombre_producto')} "
                    f"(${item.get('subtotal')})"
                )
