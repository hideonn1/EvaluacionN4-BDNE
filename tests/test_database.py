import os
from unittest.mock import MagicMock

import pytest
from pymongo.errors import ConnectionFailure

import database


@pytest.fixture(autouse=True)
def reset_singleton():
    database._cliente_mongo = None
    yield
    database._cliente_mongo = None


def test_obtener_conexion_exitosa(mocker):
    mocker.patch.dict(
        os.environ,
        {
            "MONGO_ROOT_USERNAME": "test_user",
            "MONGO_ROOT_PASSWORD": "test_password",
            "MONGO_DATABASE": "test_db",
            "MONGO_URI": "mongodb://localhost:27017",
        },
    )

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


def test_obtener_conexion_reutiliza_singleton(mocker):
    mock_client_instance = MagicMock()
    mock_db = MagicMock()
    mock_client_instance.__getitem__.return_value = mock_db
    mock_client_instance.admin.command.return_value = {"ok": 1}

    mocker.patch("database.MongoClient", return_value=mock_client_instance)

    # Primera llamada
    db1 = database.obtener_conexion_db()
    # Segunda llamada
    db2 = database.obtener_conexion_db()

    assert db1 is not None
    assert db2 is not None
    assert db1 == db2

    assert database.MongoClient.call_count == 1
