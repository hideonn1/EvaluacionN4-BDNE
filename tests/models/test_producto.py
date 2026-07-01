from unittest.mock import MagicMock

import pytest
from bson.objectid import ObjectId

from models.producto import Producto, RepositorioProductos


@pytest.fixture
def mock_db():
    return MagicMock()


@pytest.fixture
def repo_productos(mock_db):
    return RepositorioProductos(mock_db)


def test_producto_a_documento():
    p = Producto("Laptop", 1500.0, 10, "Electronica")
    doc = p.a_documento()
    assert doc == {
        "nombre": "Laptop",
        "precio": 1500.0,
        "stock": 10,
        "categoria": "Electronica",
    }


def test_repositorio_validar_exitoso(repo_productos):
    datos = {"nombre": "Mouse", "precio": 25.0, "stock": 50}
    assert repo_productos.validar(datos) is True


def test_repositorio_validar_falla_sin_nombre(repo_productos):
    datos = {"precio": 25.0, "stock": 50}
    assert repo_productos.validar(datos) is False


def test_repositorio_validar_falla_precio_negativo(repo_productos):
    datos = {"nombre": "Mouse", "precio": -5.0, "stock": 50}
    assert repo_productos.validar(datos) is False


def test_repositorio_validar_falla_stock_negativo(repo_productos):
    datos = {"nombre": "Mouse", "precio": 25.0, "stock": -1}
    assert repo_productos.validar(datos) is False


def test_repositorio_crear_exitoso(repo_productos, mocker):
    mocker.patch.object(repo_productos, "insertar", return_value="some_id")
    p = Producto("Teclado", 50.0, 20)
    assert repo_productos.crear(p) is True


def test_repositorio_crear_falla_validacion(repo_productos, mocker):
    mocker.patch.object(repo_productos, "insertar")
    p = Producto("", -10, -5)  # Invalid product
    assert repo_productos.crear(p) is False
    repo_productos.insertar.assert_not_called()


def test_descontar_stock_exitoso(repo_productos):
    valid_id = str(ObjectId())
    # Mock _coleccion.update_one
    mock_update = MagicMock()
    mock_update.modified_count = 1
    repo_productos._coleccion.update_one.return_value = mock_update

    assert repo_productos.descontar_stock(valid_id, 2) is True
    repo_productos._coleccion.update_one.assert_called_once()


def test_descontar_stock_falla_id_invalido(repo_productos):
    assert repo_productos.descontar_stock("invalid_id", 2) is False


def test_eliminar_por_id_exitoso(repo_productos, mocker):
    valid_id = str(ObjectId())
    mocker.patch.object(repo_productos, "eliminar_uno", return_value=True)

    assert repo_productos.eliminar_por_id(valid_id) is True
    repo_productos.eliminar_uno.assert_called_once()


def test_eliminar_por_id_falla_id_invalido(repo_productos, mocker):
    mocker.patch.object(repo_productos, "eliminar_uno")
    assert repo_productos.eliminar_por_id("invalid_id") is False
    repo_productos.eliminar_uno.assert_not_called()
