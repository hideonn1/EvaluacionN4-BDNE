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
            self._vista.mostrar_mensaje("Cliente eliminado.")
        else:
            self._vista.mostrar_error(
                "No se encontró el cliente o no se pudo eliminar."
            )
