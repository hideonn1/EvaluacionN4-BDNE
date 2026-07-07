from dataclasses import dataclass, field
from typing import Optional

from bson.objectid import ObjectId
from pymongo.errors import PyMongoError

from models.base_model import RepositorioBase


@dataclass
class Producto:
    nombre: str
    precio: float
    stock: int
    categoria: Optional[str] = None
    _id: Optional[str] = field(default=None, repr=False)

    def a_documento(self) -> dict:
        return {
            "nombre": self.nombre.strip(),
            "precio": float(self.precio),
            "stock": int(self.stock),
            "categoria": self.categoria,
        }

    @staticmethod
    def desde_documento(doc: dict) -> "Producto":
        return Producto(
            nombre=doc.get("nombre", ""),
            precio=doc.get("precio", 0.0),
            stock=doc.get("stock", 0),
            categoria=doc.get("categoria"),
            _id=doc.get("_id"),
        )


class RepositorioProductos(RepositorioBase):
    def __init__(self, db):
        super().__init__(db, "productos")

    def validar(self, datos: dict) -> bool:
        nombre = str(datos.get("nombre", ""))
        if not nombre.strip():
            print("[Validación] El nombre del producto es obligatorio.")
            return False
        if nombre.strip().isdigit():
            print("[Validación] El nombre del producto no puede contener únicamente números.")
            return False
        if datos.get("precio", -1) <= 0:
            print("[Validación] El precio debe ser mayor a 0.")
            return False
        if datos.get("stock", -1) <= 0:
            print("[Validación] El stock debe ser mayor a 0.")
            return False
        return True

    def crear(self, producto: Producto) -> bool:
        documento = producto.a_documento()
        if not self.validar(documento):
            return False
        return self.insertar(documento) is not None

    def listar_disponibles(self) -> list:
        return self.buscar_todos({"stock": {"$gt": 0}})

    def listar_todos(self) -> list:
        return self.buscar_todos()

    def buscar_por_id(self, id_producto: str) -> Optional[dict]:
        if not ObjectId.is_valid(id_producto):
            print(
                f"[Validación] El ID '{id_producto}' no tiene un formato NoSQL válido."
            )
            return None
        return self.buscar_uno({"_id": ObjectId(id_producto)})

    def incrementar_stock(self, id_producto: str, cantidad: int) -> bool:
        if not ObjectId.is_valid(id_producto):
            return False
        try:
            resultado = self._coleccion.update_one(
                {"_id": ObjectId(id_producto)}, {"$inc": {"stock": cantidad}}
            )
            return resultado.modified_count > 0
        except PyMongoError as e:
            print(f"[Error] No se pudo revertir stock del producto {id_producto}: {e}")
            return False

    def descontar_stock(self, id_producto: str, cantidad: int) -> bool:
        if not ObjectId.is_valid(id_producto):
            print(
                f"[Validación] El ID '{id_producto}' no tiene un formato NoSQL válido."
            )
            return False
        try:
            resultado = self._coleccion.update_one(
                {"_id": ObjectId(id_producto), "stock": {"$gte": cantidad}},
                {"$inc": {"stock": -cantidad}},
            )
            return resultado.modified_count > 0
        except PyMongoError as e:
            print(f"[Error] No se pudo descontar stock del producto {id_producto}: {e}")
            return False

    def eliminar_por_id(self, id_producto_str: str) -> bool:
        if not ObjectId.is_valid(id_producto_str):
            print(
                f"[Validación] El formato del ID '{id_producto_str}' no corresponde "
                "a una estructura NoSQL válida."
            )
            return False
        return self.eliminar_uno({"_id": ObjectId(id_producto_str)})

    def actualizar_por_id(self, id_producto_str: str, cambios: dict) -> bool:
        """Actualiza campos del producto. No permite modificar _id."""
        if not ObjectId.is_valid(id_producto_str):
            print(
                f"[Validación] El ID '{id_producto_str}' no tiene un formato NoSQL válido."
            )
            return False
        return self.actualizar_uno({"_id": ObjectId(id_producto_str)}, cambios)
