import re
from dataclasses import dataclass, field
from typing import Optional

from models.base_model import RepositorioBase


@dataclass
class Cliente:
    rut: str
    nombre: str
    email: str
    telefono: Optional[str] = None
    direccion: Optional[str] = None
    _id: Optional[str] = field(default=None, repr=False)

    def a_documento(self) -> dict:
        return {
            "rut": self.rut.strip(),
            "nombre": self.nombre.strip(),
            "email": self.email.strip().lower(),
            "telefono": self.telefono,
            "direccion": self.direccion,
        }

    @staticmethod
    def desde_documento(doc: dict) -> "Cliente":
        return Cliente(
            rut=doc.get("rut", ""),
            nombre=doc.get("nombre", ""),
            email=doc.get("email", ""),
            telefono=doc.get("telefono"),
            direccion=doc.get("direccion"),
            _id=doc.get("_id"),
        )


class RepositorioClientes(RepositorioBase):
    PATRON_RUT = re.compile(r"^\d{7,8}-[\dkK]$")
    PATRON_EMAIL = re.compile(r"^[^@\s]+@[^@\s]+\.[^@\s]+$")
    PATRON_TELEFONO = re.compile(r"^\+?[\d\s\(\)\-]{7,20}$")

    def __init__(self, db):
        super().__init__(db, "clientes")

    def validar(self, datos: dict) -> bool:
        rut = datos.get("rut", "")
        email = datos.get("email", "")
        telefono = datos.get("telefono")
        if not datos.get("nombre"):
            print("[Validación] El nombre del cliente es obligatorio.")
            return False
        if not self.PATRON_RUT.match(rut):
            return False
        if not self.PATRON_EMAIL.match(email):
            print(f"[Validación] Email '{email}' no tiene un formato válido.")
            return False
        if telefono and not self.PATRON_TELEFONO.match(telefono):
            print(
                f"[Validación] Teléfono '{telefono}' no es válido. "
                "Use solo dígitos, espacios, guíones o +."
            )
            return False
        return True

    def crear(self, cliente: Cliente) -> bool:
        documento = cliente.a_documento()
        if not self.validar(documento):
            return False
        if self.buscar_por_rut(documento["rut"]) is not None:
            print(f"[Aviso] Ya existe un cliente con RUT {documento['rut']}.")
            return False
        return self.insertar(documento) is not None

    def buscar_por_rut(self, rut_cliente: str) -> Optional[dict]:
        return self.buscar_uno({"rut": rut_cliente.strip()})

    def listar_todos(self) -> list:
        return self.buscar_todos()

    def actualizar_datos(self, rut_cliente: str, cambios: dict) -> bool:
        return self.actualizar_uno({"rut": rut_cliente.strip()}, cambios)

    def eliminar_por_rut(self, rut_cliente: str) -> bool:
        return self.eliminar_uno({"rut": rut_cliente.strip()})
