from views.vista_base import VistaBase


class VistaPedido(VistaBase):
    def menu(self) -> str:
        self.mostrar_titulo("GESTIÓN DE PEDIDOS")
        return self.pedir_opcion(
            {
                "1": "Crear pedido",
                "2": "Listar pedidos activos",
                "3": "Listar todos los pedidos",
                "4": "Cambiar estado de un pedido",
                "5": "Eliminar pedido",
                "0": "Volver",
            }
        )

    def solicitar_rut_cliente(self) -> str:
        return self.pedir_texto("RUT del cliente")

    def solicitar_codigo_pedido_nuevo(self) -> str:
        return self.pedir_texto("Código para el nuevo pedido (ej: PED-001)")

    def solicitar_id_producto_para_item(self) -> str:
        return self.pedir_texto("ID del producto a agregar (ENTER para terminar)")

    def solicitar_cantidad(self) -> int:
        return int(self.pedir_numero("Cantidad", tipo=int))

    def confirmar(self, pregunta: str) -> bool:
        respuesta = input(f"{pregunta} (s/n): ").strip().lower()
        return respuesta in ("s", "si", "sí", "y", "yes")

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
