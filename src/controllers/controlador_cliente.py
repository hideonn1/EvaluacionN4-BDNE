from models.cliente import Cliente, RepositorioClientes
from views.vista_cliente import VistaCliente


class ControladorCliente:
    # Maneja el submenú y las acciones CRUD de clientes.

    def __init__(self, db):
        self._repositorio = RepositorioClientes(db)
        self._vista = VistaCliente()

    def ejecutar(self) -> None:
        acciones = {
            "1": self._registrar,
            "2": self._buscar,
            "3": self._listar,
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
