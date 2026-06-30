from controllers.controlador_cliente import ControladorCliente
from controllers.controlador_pedido import ControladorPedido
from controllers.controlador_producto import ControladorProducto
from views.vista_base import VistaBase


class ControladorPrincipal:
    # Punto de entrada de la lógica de la aplicación (composición de controladores).
    def __init__(self, db):
        self._vista = VistaBase()
        self._controlador_cliente = ControladorCliente(db)
        self._controlador_producto = ControladorProducto(db)
        self._controlador_pedido = ControladorPedido(db)

    def ejecutar(self) -> None:
        acciones = {
            "1": self._controlador_cliente.ejecutar,
            "2": self._controlador_producto.ejecutar,
            "3": self._controlador_pedido.ejecutar,
        }
        while True:
            self._vista.mostrar_titulo("SISTEMA COMERCIOTECH")
            opcion = self._vista.pedir_opcion(
                {
                    "1": "Gestión de clientes",
                    "2": "Gestión de productos",
                    "3": "Gestión de pedidos",
                    "0": "Salir",
                }
            )
            if opcion == "0":
                self._vista.mostrar_mensaje("Hasta luego.")
                return
            accion = acciones.get(opcion)
            if accion:
                accion()
            else:
                self._vista.mostrar_error("Opción inválida.")
