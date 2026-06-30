from models.pedido import RepositorioPedidos
from views.vista_pedido import VistaPedido


class ControladorPedido:
    # Maneja el submenú y las acciones CRUD de pedidos.

    def __init__(self, db):
        self._repositorio = RepositorioPedidos(db)
        self._vista = VistaPedido()

    def ejecutar(self) -> None:
        acciones = {
            "1": self._listar_activos,
            "2": self._listar_todos,
            "3": self._cambiar_estado,
            "4": self._eliminar,
        }
        while True:
            opcion = self._vista.menu()
            if opcion == "0":
                return
            accion = acciones.get(opcion)
            if accion:
                accion()
            else:
                self._vista.mostrar_error("Opción inválida.")

    def _listar_activos(self) -> None:
        self._vista.mostrar_lista_pedidos(self._repositorio.obtener_activos())

    def _listar_todos(self) -> None:
        self._vista.mostrar_lista_pedidos(self._repositorio.listar_todos())

    def _cambiar_estado(self) -> None:
        codigo = self._vista.solicitar_codigo()
        estado = self._vista.solicitar_estado()
        if self._repositorio.actualizar_estado(codigo, estado):
            self._vista.mostrar_mensaje("Estado actualizado.")
        else:
            self._vista.mostrar_error("No se pudo actualizar el estado del pedido.")

    def _eliminar(self) -> None:
        codigo = self._vista.solicitar_codigo()
        if self._repositorio.eliminar_por_codigo(codigo):
            self._vista.mostrar_mensaje("Pedido eliminado.")
        else:
            self._vista.mostrar_error("No se encontró el pedido o no se pudo eliminar.")
