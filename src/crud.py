from bson.objectid import ObjectId
from pymongo.errors import PyMongoError

from database import obtener_conexion_db

db = obtener_conexion_db()


def buscar_cliente_por_rut(rut_cliente: str):
    try:
        cliente = db.clientes.find_one({"rut": rut_cliente.strip()})
        return cliente
    except PyMongoError as e:
        print(f"Error de lectura en la colección clientes: {e}")
        return None


def listar_productos_en_stock():
    try:
        return list(db.productos.find({"stock": {"$gt": 0}}))
    except PyMongoError as e:
        print(f"Fallo al consultar catálogo de productos: {e}")
        return []


def obtener_pedidos_activos():
    try:
        return list(db.pedidos.find())
    except PyMongoError as e:
        print(f"Error al extraer documentos de pedidos: {e}")
        return []


def eliminar_producto_por_id(id_producto_str: str) -> bool:
    if not ObjectId.is_valid(id_producto_str):
        print(
            f"El formato del ID '{id_producto_str}' no corresponde a una estructura NoSQL válida."
        )
        return False

    try:
        resultado = db.productos.delete_one({"_id": ObjectId(id_producto_str)})
        if resultado.deleted_count > 0:
            print(f"[+] Documento de producto [{id_producto_str}] eliminado con éxito.")
            return True
        print(f"[-] No se encontró ningún producto con el ID especificado.")
        return False
    except PyMongoError as e:
        print(f"Error fatal de persistencia durante el borrado: {e}")
        return False


def eliminar_pedido_por_codigo(codigo_pedido: str) -> bool:
    try:
        resultado = db.pedidos.delete_one({"codigo_pedido": codigo_pedido.strip()})
        return resultado.deleted_count > 0
    except PyMongoError as e:
        print(f"Fallo al intentar remover el pedido {codigo_pedido}: {e}")
        return False
