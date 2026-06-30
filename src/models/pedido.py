from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import List, Optional

from models.base_model import RepositorioBase


@dataclass
class ItemPedido:
    producto_id: str
    nombre_producto: str
    cantidad: int
    precio_unitario: float

    def a_documento(self) -> dict:
        return {
            "producto_id": self.producto_id,
            "nombre_producto": self.nombre_producto,
            "cantidad": self.cantidad,
            "precio_unitario": self.precio_unitario,
            "subtotal": round(self.cantidad * self.precio_unitario, 2),
        }


@dataclass
class Pedido:
    codigo_pedido: str
    rut_cliente: str
    items: List[ItemPedido] = field(default_factory=list)
    estado: str = "pendiente"
    fecha_creacion: datetime = field(default_factory=lambda: datetime.now(timezone.utc))

    def a_documento(self) -> dict:
        return {
            "codigo_pedido": self.codigo_pedido.strip(),
            "rut_cliente": self.rut_cliente.strip(),
            "items": [item.a_documento() for item in self.items],
            "total": round(sum(i.cantidad * i.precio_unitario for i in self.items), 2),
            "estado": self.estado,
            "fecha_creacion": self.fecha_creacion,
        }


class RepositorioPedidos(RepositorioBase):
    ESTADOS_VALIDOS = {"pendiente", "procesando", "enviado", "entregado", "cancelado"}

    def __init__(self, db):
        super().__init__(db, "pedidos")

    def validar(self, datos: dict) -> bool:
        if not datos.get("codigo_pedido"):
            print("[Validación] El código de pedido es obligatorio.")
            return False
        if not datos.get("rut_cliente"):
            print("[Validación] El pedido debe estar asociado a un cliente (RUT).")
            return False
        if not datos.get("items"):
            print("[Validación] El pedido debe contener al menos un producto.")
            return False
        if datos.get("estado") not in self.ESTADOS_VALIDOS:
            print(f"[Validación] Estado inválido: {datos.get('estado')}.")
            return False
        return True

    def crear(self, pedido: Pedido) -> bool:
        documento = pedido.a_documento()
        if not self.validar(documento):
            return False
        if self.buscar_uno({"codigo_pedido": documento["codigo_pedido"]}):
            print(
                f"[Aviso] Ya existe un pedido con código {documento['codigo_pedido']}."
            )
            return False
        return self.insertar(documento) is not None

    def obtener_activos(self) -> list:
        """Pedidos que aún no han sido entregados ni cancelados."""
        return self.buscar_todos({"estado": {"$nin": ["entregado", "cancelado"]}})

    def listar_todos(self) -> list:
        return self.buscar_todos()

    def actualizar_estado(self, codigo_pedido: str, nuevo_estado: str) -> bool:
        if nuevo_estado not in self.ESTADOS_VALIDOS:
            print(f"[Validación] Estado inválido: {nuevo_estado}.")
            return False
        return self.actualizar_uno(
            {"codigo_pedido": codigo_pedido.strip()}, {"estado": nuevo_estado}
        )

    def eliminar_por_codigo(self, codigo_pedido: str) -> bool:
        return self.eliminar_uno({"codigo_pedido": codigo_pedido.strip()})
