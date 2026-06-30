from abc import ABC, abstractmethod
from typing import Any, Optional

from pymongo.collection import Collection
from pymongo.errors import PyMongoError


class RepositorioBase(ABC):
    def __init__(self, db, nombre_coleccion: str):
        self._db = db
        self._coleccion: Collection = db[nombre_coleccion]
        self._nombre_coleccion = nombre_coleccion

    def insertar(self, documento: dict) -> Optional[Any]:
        try:
            resultado = self._coleccion.insert_one(documento)
            return resultado.inserted_id
        except PyMongoError as e:
            print(f"[Error] No se pudo insertar en '{self._nombre_coleccion}': {e}")
            return None

    def buscar_uno(self, filtro: dict) -> Optional[dict]:
        try:
            return self._coleccion.find_one(filtro)
        except PyMongoError as e:
            print(f"[Error] Falla de lectura en '{self._nombre_coleccion}': {e}")
            return None

    def buscar_todos(self, filtro: Optional[dict] = None) -> list:
        try:
            return list(self._coleccion.find(filtro or {}))
        except PyMongoError as e:
            print(f"[Error] Falla al listar '{self._nombre_coleccion}': {e}")
            return []

    def actualizar_uno(self, filtro: dict, cambios: dict) -> bool:
        try:
            resultado = self._coleccion.update_one(filtro, {"$set": cambios})
            return resultado.modified_count > 0
        except PyMongoError as e:
            print(f"[Error] Falla al actualizar '{self._nombre_coleccion}': {e}")
            return False

    def eliminar_uno(self, filtro: dict) -> bool:
        try:
            resultado = self._coleccion.delete_one(filtro)
            return resultado.deleted_count > 0
        except PyMongoError as e:
            print(f"[Error] Falla al eliminar en '{self._nombre_coleccion}': {e}")
            return False

    @abstractmethod
    def validar(self, datos: dict) -> bool:
        raise NotImplementedError
