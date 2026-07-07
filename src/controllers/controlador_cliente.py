from models.cliente import Cliente, RepositorioClientes
from models.pedido import RepositorioPedidos
from views.vista_cliente import VistaCliente


class ControladorCliente:
    # Maneja el submenú y las acciones CRUD de clientes.

    def __init__(self, db, rol: str):
        self._repositorio = RepositorioClientes(db)
        self._repo_pedidos = RepositorioPedidos(db)
        self._vista = VistaCliente()
        self._rol = rol

    def ejecutar(self) -> None:
        acciones = {}
        opciones = {}

        if self._rol in ["1", "2"]:
            acciones["1"] = self._registrar
            opciones["1"] = "Registrar cliente"

        if self._rol in ["1", "2", "3"]:
            acciones["2"] = self._buscar
            opciones["2"] = "Buscar cliente por RUT"
            acciones["3"] = self._listar
            opciones["3"] = "Listar clientes"

        if self._rol in ["1", "2"]:
            acciones["4"] = self._eliminar
            opciones["4"] = "Eliminar cliente"
            acciones["5"] = self._modificar
            opciones["5"] = "Modificar cliente"

        opciones["0"] = "Volver"

        while True:
            self._vista.mostrar_titulo("GESTIÓN DE CLIENTES")
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
        datos = self._vista.solicitar_datos_cliente()
        cliente = Cliente(**datos)
        if self._repositorio.crear(cliente):
            self._vista.mostrar_mensaje("Cliente registrado correctamente.")
        else:
            self._vista.mostrar_error("No se pudo registrar el cliente.")

    def _buscar(self) -> None:
        rut = self._vista.solicitar_rut()
        cliente = self._repositorio.buscar_por_rut(rut)
        self._vista.mostrar_cliente(cliente)

    def _listar(self) -> None:
        clientes = self._repositorio.listar_todos()
        self._vista.mostrar_lista_clientes(clientes)

    def _eliminar(self) -> None:
        rut = self._vista.solicitar_rut()

        if self._repo_pedidos.buscar_uno({"rut_cliente": rut.strip()}):
            self._vista.mostrar_error(
                "No se puede eliminar el cliente porque tiene pedidos asociados."
            )
            return

        if self._repositorio.eliminar_por_rut(rut):
            self._vista.mostrar_baja("Cliente eliminado.")
        else:
            self._vista.mostrar_error(
                "No se encontró el cliente o no se pudo eliminar."
            )

    def _modificar(self) -> None:
        rut = self._vista.solicitar_rut()
        cliente_actual = self._repositorio.buscar_por_rut(rut)
        if not cliente_actual:
            self._vista.mostrar_error("No se encontró ningún cliente con ese RUT.")
            return

        self._vista.mostrar_titulo("DATOS ACTUALES DEL CLIENTE")
        self._vista.mostrar_cliente(cliente_actual)

        cambios = self._vista.solicitar_datos_modificacion(cliente_actual)

        if not cambios:
            self._vista.mostrar_mensaje("No se realizaron cambios.")
            return

        datos_validar = {
            "rut": cliente_actual.get("rut"),
            "nombre": cambios.get("nombre", cliente_actual.get("nombre")),
            "email": cambios.get("email", cliente_actual.get("email")),
            "telefono": cambios.get("telefono", cliente_actual.get("telefono")),
            "direccion": cambios.get("direccion", cliente_actual.get("direccion")),
        }
        if not self._repositorio.validar(datos_validar):
            self._vista.mostrar_error("Los datos ingresados no son válidos.")
            return

        if "email" in cambios:
            existente = self._repositorio.buscar_uno(
                {"email": cambios["email"].strip().lower()}
            )
            if existente and existente.get("rut") != rut:
                self._vista.mostrar_error(
                    f"El email '{cambios['email']}' ya está en uso por otro cliente."
                )
                return

        if self._repositorio.actualizar_datos(rut, cambios):
            self._vista.mostrar_mensaje("Cliente actualizado correctamente.")

            cliente_actualizado = self._repositorio.buscar_por_rut(rut)
            if cliente_actualizado:
                self._vista.mostrar_titulo("DATOS GUARDADOS")
                self._vista.mostrar_cliente(cliente_actualizado)
        else:
            self._vista.mostrar_error("No se pudo actualizar el cliente.")
