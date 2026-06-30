from models.producto import Producto, RepositorioProductos
from views.vista_producto import VistaProducto


class ControladorProducto:
    # Maneja el submenú y las acciones CRUD de productos.
    def __init__(self, db):
        self._repositorio = RepositorioProductos(db)
        self._vista = VistaProducto()

    def ejecutar(self) -> None:
        acciones = {
            "1": self._registrar,
            "2": self._listar_en_stock,
            "3": self._eliminar,
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

    def _registrar(self) -> None:
        datos = self._vista.solicitar_datos_producto()
        producto = Producto(**datos)
        if self._repositorio.crear(producto):
            self._vista.mostrar_mensaje("Producto registrado correctamente.")
        else:
            self._vista.mostrar_error("No se pudo registrar el producto.")

    def _listar_en_stock(self) -> None:
        self._vista.mostrar_lista_productos(self._repositorio.listar_disponibles())

    def _eliminar(self) -> None:
        id_producto = self._vista.solicitar_id()
        if self._repositorio.eliminar_por_id(id_producto):
            self._vista.mostrar_mensaje("Producto eliminado.")
        else:
            self._vista.mostrar_error(
                "No se encontró el producto o no se pudo eliminar."
            )
