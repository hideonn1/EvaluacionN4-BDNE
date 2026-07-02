import os
import sys
from pathlib import Path
from typing import Optional
from urllib.parse import quote_plus

from dotenv import load_dotenv
from pymongo import MongoClient
from pymongo.database import Database
from pymongo.errors import ConfigurationError, ConnectionFailure, PyMongoError

ruta_env = Path(__file__).resolve().parent.parent / ".env"
load_dotenv(dotenv_path=ruta_env)

_cliente_mongo: Optional[MongoClient] = None
_rol_actual: Optional[str] = None

ROLES = {
    "1": {
        "nombre": "Administrador (root)",
        "var_user": "MONGO_ROOT_USERNAME",
        "var_pass": "MONGO_ROOT_PASSWORD",
        "auth_source": "admin",
    },
    "2": {
        "nombre": "Aplicación (readWrite)",
        "var_user": "APP_USERNAME",
        "var_pass": "APP_PASSWORD",
        "auth_source": None,
    },
    "3": {
        "nombre": "Auditor (solo lectura)",
        "var_user": "AUDITOR_USERNAME",
        "var_pass": "AUDITOR_PASSWORD",
        "auth_source": None,
    },
    "4": {
        "nombre": "Monitor (clusterMonitor)",
        "var_user": "MONITOR_USERNAME",
        "var_pass": "MONITOR_PASSWORD",
        "auth_source": "admin",
    },
}


def obtener_conexion_db(rol: str = "2") -> Optional[Database]:
    global _cliente_mongo, _rol_actual

    db_name = os.getenv("MONGO_DATABASE", "comerciotech_db")
    config_rol = ROLES.get(rol, ROLES["2"])

    if _cliente_mongo is not None and _rol_actual == rol:
        try:
            _cliente_mongo.admin.command("ping")
            return _cliente_mongo[db_name]
        except PyMongoError:
            _cliente_mongo = None

    usuario = os.getenv(config_rol["var_user"])
    password = os.getenv(config_rol["var_pass"])
    if not usuario or not password:
        print(
            f"(Error de Configuración) Faltan credenciales para el rol "
            f"'{config_rol['nombre']}' ({config_rol['var_user']}/{config_rol['var_pass']} en .env).",
            file=sys.stderr,
        )
        return None

    auth_source = config_rol["auth_source"] or db_name
    host = os.getenv("MONGO_HOST", "mongodb")
    puerto = os.getenv("MONGO_PORT", "27017")

    mongo_uri = (
        f"mongodb://{quote_plus(usuario)}:{quote_plus(password)}"
        f"@{host}:{puerto}/?authSource={auth_source}"
    )

    max_pool = int(os.getenv("MONGO_MAX_POOL_SIZE", "50"))
    min_pool = int(os.getenv("MONGO_MIN_POOL_SIZE", "10"))
    timeout_ms = int(os.getenv("MONGO_TIMEOUT_MS", "5000"))
    usar_tls = os.getenv("MONGO_USE_TLS", "false").lower() == "true"

    try:
        _cliente_mongo = MongoClient(
            mongo_uri,
            serverSelectionTimeoutMS=timeout_ms,
            connectTimeoutMS=timeout_ms,
            maxPoolSize=max_pool,
            minPoolSize=min_pool,
            tls=usar_tls,
        )
        _cliente_mongo.admin.command("ping")
        _rol_actual = rol
        print(
            f"[Conexión Exitosa] Conectado a MongoDB como '{config_rol['nombre']}'. "
            f"Pool configurado: {min_pool}-{max_pool} conexiones."
        )
        return _cliente_mongo[db_name]
    except ConnectionFailure as e:
        print(
            f"(Error Crítico de Conexión) El servidor MongoDB no responde.\n"
            f"Host objetivo: {host}:{puerto}\nDetalle: {e}",
            file=sys.stderr,
        )
    except ConfigurationError as e:
        print(
            f"(Error de Configuración) Error en los parámetros de la URI de MongoDB.\n"
            f"Detalle: {e}",
            file=sys.stderr,
        )
    except Exception as e:
        print(
            f"(Error Inesperado) Fallo al intentar conectar a la base de datos.\n"
            f"Detalle: {e}",
            file=sys.stderr,
        )
    return None


def autenticar(usuario: str, password: str) -> Optional[str]:
    for clave, info in ROLES.items():
        usuario_esperado = os.getenv(info["var_user"])
        password_esperado = os.getenv(info["var_pass"])
        if (
            usuario_esperado
            and usuario == usuario_esperado
            and password == password_esperado
        ):
            return clave
    return None
