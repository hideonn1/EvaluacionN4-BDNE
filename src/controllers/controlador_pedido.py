from models.cliente import RepositorioClientes
from models.pedido import ItemPedido, Pedido, RepositorioPedidos
from models.producto import RepositorioProductos
from views.vista_pedido import VistaPedido
from views.vista_producto import VistaProducto


class ControladorPedido:
    # Maneja el submenú y las acciones CRUD de pedidos.

    def __init__(self, db, rol: str):
        self._repositorio = RepositorioPedidos(db)
        self._repo_clientes = RepositorioClientes(db)
        self._repo_productos = RepositorioProductos(db)
        self._vista = VistaPedido()
        self._vista_producto = VistaProducto()
        self._rol = rol

    def ejecutar(self) -> None:
        acciones = {}
        opciones = {}

        if self._rol in ["1", "2"]:
            acciones["1"] = self._crear
            opciones["1"] = "Crear pedido"

        if self._rol in ["1", "2", "3"]:
            acciones["2"] = self._listar_activos
            opciones["2"] = "Listar pedidos activos"
            acciones["3"] = self._listar_todos
            opciones["3"] = "Listar todos los pedidos"

        if self._rol in ["1", "2"]:
            acciones["4"] = self._cambiar_estado
            opciones["4"] = "Cambiar estado de un pedido"
            acciones["5"] = self._eliminar
            opciones["5"] = "Eliminar pedido"

        opciones["0"] = "Volver"

        while True:
            self._vista.mostrar_titulo("GESTIÓN DE PEDIDOS")
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

    def _crear(self) -> None:
        rut = self._vista.solicitar_rut_cliente()
        if not self._repo_clientes.buscar_por_rut(rut):
            self._vista.mostrar_error(
                f"No existe un cliente con RUT {rut}. Regístralo primero en el menú de clientes."
            )
            return

        codigo = self._vista.solicitar_codigo_pedido_nuevo()
        if self._repositorio.buscar_uno({"codigo_pedido": codigo.strip()}):
            self._vista.mostrar_error(f"Ya existe un pedido con código {codigo}.")
            return

        items = self._armar_items()
        if not items:
            self._vista.mostrar_error(
                "El pedido no tiene productos. Operación cancelada."
            )
            return

        pedido = Pedido(codigo_pedido=codigo, rut_cliente=rut, items=items)
        if self._repositorio.crear(pedido):
            self._vista.mostrar_mensaje(f"Pedido {codigo} creado correctamente.")
        else:
            self._vista.mostrar_error(
                "No se pudo crear el pedido. Revirtiendo stock descontado."
            )
            self._revertir_descuentos(items)

    def _armar_items(self) -> list:
        """Bucle interactivo: selecciona productos, valida stock y lo descuenta."""
        items: list[ItemPedido] = []
        try:
            while True:
                self._vista_producto.mostrar_lista_productos(
                    self._repo_productos.listar_disponibles()
                )
                id_producto = self._vista.solicitar_id_producto_para_item()
                if not id_producto:
                    break

                producto = self._repo_productos.buscar_por_id(id_producto)
                if not producto:
                    self._vista.mostrar_error("Producto no encontrado.")
                    continue

                cantidad = self._vista.solicitar_cantidad()
                if cantidad <= 0:
                    self._vista.mostrar_error("La cantidad debe ser mayor a 0.")
                    continue

                stock_actual = producto.get("stock", 0)
                if cantidad > stock_actual:
                    mensaje = (
                        f"Solo quedan {stock_actual} y escogió {cantidad}, si acepta se "
                        f"incluirán todo el stock, en caso contrario se revertirá esta acción"
                    )
                    if self._vista.confirmar(mensaje):
                        cantidad = stock_actual
                    else:
                        self._vista.mostrar_error("Operación revertida.")
                        continue

                if not self._repo_productos.descontar_stock(id_producto, cantidad):
                    self._vista.mostrar_error("Stock insuficiente para esa cantidad.")
                    continue

                items.append(
                    ItemPedido(
                        producto_id=id_producto,
                        nombre_producto=producto["nombre"],
                        cantidad=cantidad,
                        precio_unitario=producto["precio"],
                    )
                )
                self._vista.mostrar_mensaje(
                    f"Agregado: {cantidad}x {producto['nombre']}."
                )

                if not self._vista.confirmar("¿Agregar otro producto?"):
                    break
            return items
        except KeyboardInterrupt:
            self._revertir_descuentos(items)
            raise

    def _revertir_descuentos(self, items: list) -> None:
        """Devuelve el stock descontado cuando la creación del pedido falla."""
        for item in items:
            self._repo_productos.incrementar_stock(item.producto_id, item.cantidad)

    def _listar_activos(self) -> None:
        self._vista.mostrar_lista_pedidos(self._repositorio.obtener_activos())

    def _listar_todos(self) -> None:
        self._vista.mostrar_lista_pedidos(self._repositorio.listar_todos())

    def _cambiar_estado(self) -> None:
        codigo = self._vista.solicitar_codigo()

        pedido_actual = self._repositorio.buscar_uno({"codigo_pedido": codigo.strip()})
        if not pedido_actual:
            self._vista.mostrar_error("No se encontró ningún pedido con ese código.")
            return

        estado = self._vista.solicitar_estado()

        if pedido_actual.get("estado") == "cancelado" and estado != "cancelado":
            self._vista.mostrar_error(
                "No se puede cambiar el estado de un pedido que ya está cancelado."
            )
            return

        if pedido_actual.get("estado") == "cancelado" and estado == "cancelado":
            self._vista.mostrar_mensaje("El pedido ya se encuentra cancelado.")
            return

        if self._repositorio.actualizar_estado(codigo, estado):
            self._vista.mostrar_mensaje("Estado actualizado.")
            if estado == "cancelado":
                for item in pedido_actual.get("items", []):
                    self._repo_productos.incrementar_stock(
                        item["producto_id"], item["cantidad"]
                    )
                self._vista.mostrar_mensaje("Stock de los productos restituido.")
        else:
            self._vista.mostrar_error("No se pudo actualizar el estado del pedido.")

    def _eliminar(self) -> None:
        codigo = self._vista.solicitar_codigo()

        pedido_actual = self._repositorio.buscar_uno({"codigo_pedido": codigo.strip()})

        if self._repositorio.eliminar_por_codigo(codigo):
            self._vista.mostrar_mensaje("Pedido eliminado.")
            if pedido_actual and pedido_actual.get("estado") != "cancelado":
                for item in pedido_actual.get("items", []):
                    self._repo_productos.incrementar_stock(
                        item["producto_id"], item["cantidad"]
                    )
                self._vista.mostrar_mensaje("Stock de los productos restituido.")
        else:
            self._vista.mostrar_error("No se encontró el pedido o no se pudo eliminar.")
