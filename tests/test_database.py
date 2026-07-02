import os
from unittest.mock import MagicMock

import database
import pytest
from pymongo.errors import ConnectionFailure


@pytest.fixture(autouse=True)
def reset_singleton():
    database._cliente_mongo = None
    database._rol_actual = None
    yield
    database._cliente_mongo = None
    database._rol_actual = None


@pytest.fixture(autouse=True)
def credenciales_rol_app(mocker):
    # El rol por defecto ('2', aplicación) necesita estas variables presentes.
    mocker.patch.dict(
        os.environ,
        {
            "APP_USERNAME": "app_user",
            "APP_PASSWORD": "app_password",
            "MONGO_DATABASE": "test_db",
        },
    )


def test_obtener_conexion_exitosa(mocker):
    mock_client_instance = MagicMock()
    mock_db = MagicMock()
    mock_client_instance.__getitem__.return_value = mock_db
    mock_client_instance.admin.command.return_value = {"ok": 1}

    mock_mongo_client = mocker.patch(
        "database.MongoClient", return_value=mock_client_instance
    )

    db = database.obtener_conexion_db()

    assert db is not None
    mock_mongo_client.assert_called_once()
    mock_client_instance.admin.command.assert_called_with("ping")


def test_obtener_conexion_falla_conexion(mocker):
    mocker.patch(
        "database.MongoClient", side_effect=ConnectionFailure("Error de conexion")
    )

    db = database.obtener_conexion_db()

    assert db is None


def test_obtener_conexion_falla_sin_credenciales(mocker):
    # Si faltan las variables de entorno del rol, no debe intentar conectar.
    mocker.patch.dict(os.environ, {"APP_USERNAME": "", "APP_PASSWORD": ""}, clear=False)
    for var in ("APP_USERNAME", "APP_PASSWORD"):
        os.environ.pop(var, None)

    mock_mongo_client = mocker.patch("database.MongoClient")

    db = database.obtener_conexion_db(rol="2")

    assert db is None
    mock_mongo_client.assert_not_called()


def test_obtener_conexion_reutiliza_singleton(mocker):
    mock_client_instance = MagicMock()
    mock_db = MagicMock()
    mock_client_instance.__getitem__.return_value = mock_db
    mock_client_instance.admin.command.return_value = {"ok": 1}

    mocker.patch("database.MongoClient", return_value=mock_client_instance)

    db1 = database.obtener_conexion_db()
    db2 = database.obtener_conexion_db()

    assert db1 is not None
    assert db2 is not None
    assert db1 == db2
    assert database.MongoClient.call_count == 1


def test_obtener_conexion_reconecta_si_cambia_rol(mocker):
    # Pedir un rol distinto al ya autenticado debe forzar una nueva conexión.
    mocker.patch.dict(
        os.environ,
        {"MONGO_ROOT_USERNAME": "admin", "MONGO_ROOT_PASSWORD": "admin_password"},
    )
    mock_client_instance = MagicMock()
    mock_db = MagicMock()
    mock_client_instance.__getitem__.return_value = mock_db
    mock_client_instance.admin.command.return_value = {"ok": 1}
    mocker.patch("database.MongoClient", return_value=mock_client_instance)

    database.obtener_conexion_db(rol="2")  # Aplicación
    database.obtener_conexion_db(rol="1")  # Administrador (rol distinto)

    assert database.MongoClient.call_count == 2


def test_autenticar_credenciales_validas(mocker):
    mocker.patch.dict(
        os.environ,
        {"APP_USERNAME": "app_user", "APP_PASSWORD": "app_password"},
    )
    assert database.autenticar("app_user", "app_password") == "2"


def test_autenticar_credenciales_invalidas(mocker):
    mocker.patch.dict(
        os.environ,
        {"APP_USERNAME": "app_user", "APP_PASSWORD": "app_password"},
    )
    assert database.autenticar("app_user", "clave_incorrecta") is None
    assert database.autenticar("usuario_inexistente", "app_password") is None
