from models.cliente import Cliente, RepositorioClientes
from views.vista_cliente import VistaCliente


class ControladorCliente:
    # Maneja el submenú y las acciones CRUD de clientes.

    def __init__(self, db, rol: str):
        self._repositorio = RepositorioClientes(db)
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
        if self._repositorio.eliminar_por_rut(rut):
            self._vista.mostrar_baja("Cliente eliminado.")
        else:
            self._vista.mostrar_error(
                "No se encontró el cliente o no se pudo eliminar."
            )

    def _modificar(self) -> None:
        """Permite modificar los datos de un cliente existente (excepto RUT e _id)."""
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

        if "email" in cambios and not self._repositorio.PATRON_EMAIL.match(
            cambios["email"]
        ):
            self._vista.mostrar_error(
                f"Email '{cambios['email']}' no tiene un formato válido."
            )
            return

        if "telefono" in cambios and not self._repositorio.PATRON_TELEFONO.match(
            cambios["telefono"]
        ):
            self._vista.mostrar_error(
                f"Teléfono '{cambios['telefono']}' no es válido. "
                "Use solo dígitos, espacios, guiones o +."
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
