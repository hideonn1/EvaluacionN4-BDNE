from models.pedido import RepositorioPedidos
from models.producto import Producto, RepositorioProductos
from views.vista_producto import VistaProducto


class ControladorProducto:
    # Maneja el submenú y las acciones CRUD de productos.
    def __init__(self, db, rol: str):
        self._repositorio = RepositorioProductos(db)
        self._repo_pedidos = RepositorioPedidos(db)
        self._vista = VistaProducto()
        self._rol = rol

    def ejecutar(self) -> None:
        acciones = {}
        opciones = {}

        if self._rol in ["1", "2"]:
            acciones["1"] = self._registrar
            opciones["1"] = "Registrar producto"

        if self._rol in ["1", "2", "3"]:
            acciones["2"] = self._listar_en_stock
            opciones["2"] = "Listar productos en stock"

        if self._rol in ["1", "2"]:
            acciones["3"] = self._eliminar
            opciones["3"] = "Eliminar producto"
            acciones["4"] = self._modificar
            opciones["4"] = "Modificar producto"

        opciones["0"] = "Volver"

        while True:
            self._vista.mostrar_titulo("GESTIÓN DE PRODUCTOS")
            opcion = self._vista.pedir_opcion(opciones)
            if opcion == "0":
                return
            accion = acciones.get(opcion)
            if accion:
                try:
                    accion()
                except KeyboardInterrupt:
                    self._vista.mostrar_error("\nOperación cancelada por el usuario.")
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

        if self._repo_pedidos.buscar_uno({"items.producto_id": id_producto.strip()}):
            self._vista.mostrar_error(
                "No se puede eliminar el producto porque está incluido en uno o más pedidos."
            )
            return

        if self._repositorio.eliminar_por_id(id_producto):
            self._vista.mostrar_baja("Producto eliminado.")
        else:
            self._vista.mostrar_error(
                "No se encontró el producto o no se pudo eliminar."
            )

    def _modificar(self) -> None:
        """Permite modificar los datos de un producto existente (excepto _id)."""
        id_producto = self._vista.solicitar_id()
        producto_actual = self._repositorio.buscar_por_id(id_producto)
        if not producto_actual:
            self._vista.mostrar_error("No se encontró ningún producto con ese ID.")
            return

        self._vista.mostrar_titulo("DATOS ACTUALES DEL PRODUCTO")
        self._vista.mostrar_producto(producto_actual)

        cambios = self._vista.solicitar_datos_modificacion_producto(producto_actual)

        if not cambios:
            self._vista.mostrar_mensaje("No se realizaron cambios.")
            return

        # Construir documento de validación mezclando valores actuales con los cambios
        datos_validar = {
            "nombre": cambios.get("nombre", producto_actual.get("nombre")),
            "precio": cambios.get("precio", producto_actual.get("precio")),
            "stock": cambios.get("stock", producto_actual.get("stock")),
        }
        if not self._repositorio.validar(datos_validar):
            self._vista.mostrar_error("Los datos ingresados no son válidos.")
            return

        if self._repositorio.actualizar_por_id(id_producto, cambios):
            self._vista.mostrar_mensaje("Producto actualizado correctamente.")
            producto_actualizado = self._repositorio.buscar_por_id(id_producto)
            if producto_actualizado:
                self._vista.mostrar_titulo("DATOS GUARDADOS")
                self._vista.mostrar_producto(producto_actualizado)
        else:
            self._vista.mostrar_error("No se pudo actualizar el producto.")
