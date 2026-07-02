from unittest.mock import MagicMock

import pytest

from controllers.controlador_principal import ControladorPrincipal


@pytest.fixture
def mock_db():
    return MagicMock()


@pytest.fixture
def controlador(mock_db, mocker):
    mocker.patch("controllers.controlador_principal.VistaBase")
    mocker.patch("controllers.controlador_principal.ControladorCliente")
    mocker.patch("controllers.controlador_principal.ControladorProducto")
    mocker.patch("controllers.controlador_principal.ControladorPedido")
    return ControladorPrincipal(mock_db, "1")


def test_ejecutar_opcion_salir(controlador):
    controlador._vista.pedir_opcion.return_value = "0"
    controlador.ejecutar()
    controlador._vista.mostrar_mensaje.assert_called_with("Hasta luego.")


def test_ejecutar_opcion_invalida(controlador):
    controlador._vista.pedir_opcion.side_effect = ["99", "0"]
    controlador.ejecutar()
    controlador._vista.mostrar_error.assert_called_with("Opción inválida.")


def test_ejecutar_opcion_cliente(controlador):
    controlador._vista.pedir_opcion.side_effect = ["1", "0"]
    controlador.ejecutar()
    controlador._controlador_cliente.ejecutar.assert_called_once()
