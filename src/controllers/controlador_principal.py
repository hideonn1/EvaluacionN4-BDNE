from controllers.controlador_cliente import ControladorCliente
from controllers.controlador_pedido import ControladorPedido
from controllers.controlador_producto import ControladorProducto
from views.vista_base import VistaBase


class ControladorPrincipal:
    # Punto de entrada de la lógica de la aplicación (composición de controladores).
    def __init__(self, db, rol: str):
        self._db = db
        self._rol = rol
        self._vista = VistaBase()
        self._controlador_cliente = ControladorCliente(db, rol)
        self._controlador_producto = ControladorProducto(db, rol)
        self._controlador_pedido = ControladorPedido(db, rol)

    def _mostrar_estado_servidor(self) -> None:
        self._vista.mostrar_titulo("ESTADO DEL SERVIDOR MONGODB")
        try:
            status = self._db.command("serverStatus")
            print(f"Versión de MongoDB: {status.get('version')}")
            print(f"Uptime: {status.get('uptime')} segundos")
            print(f"Conexiones activas: {status.get('connections', {}).get('current')}")
            print("Estado: ONLINE\n")
        except Exception as e:
            self._vista.mostrar_error(f"Error al obtener estado del servidor: {e}")

    def ejecutar(self) -> None:
        acciones = {}
        opciones = {}
        
        if self._rol in ["1", "2", "3"]:
            acciones.update({
                "1": self._controlador_cliente.ejecutar,
                "2": self._controlador_producto.ejecutar,
                "3": self._controlador_pedido.ejecutar,
            })
            opciones.update({
                "1": "Gestión de clientes",
                "2": "Gestión de productos",
                "3": "Gestión de pedidos",
            })
            
        if self._rol in ["1", "4"]:
            acciones["4"] = self._mostrar_estado_servidor
            opciones["4"] = "Ver estado del servidor MongoDB"
            
        opciones["0"] = "Salir"
        while True:
            self._vista.mostrar_titulo("SISTEMA COMERCIOTECH")
            opcion = self._vista.pedir_opcion(opciones)
            if opcion == "0":
                self._vista.mostrar_mensaje("Hasta luego.")
                return
            accion = acciones.get(opcion)
            if accion:
                try:
                    accion()
                except KeyboardInterrupt:
                    self._vista.mostrar_error("\nOperación cancelada por el usuario.")
            else:
                self._vista.mostrar_error("Opción inválida.")
