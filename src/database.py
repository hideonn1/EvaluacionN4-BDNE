"""
=============================================================================
CT-10 y CT-11: Controlador de Conexión y Variables de Entorno
=============================================================================
Módulo encargado de gestionar la conexión segura hacia la base de datos MongoDB.
Implementa el patrón Singleton a nivel de módulo para reutilizar el pool de
conexiones, lee credenciales de forma segura desde el archivo .env, y establece
políticas de resiliencia (timeouts, connection pooling y soporte opcional TLS).

Guía de uso:
    from database import obtener_conexion_db
    db = obtener_conexion_db()
    if db is not None:
        # Operar con la base de datos
        coleccion = db["clientes"]
    else:
        # Manejar error crítico de conexión
        pass
"""

import os
import sys
from pathlib import Path
from typing import Optional

from dotenv import load_dotenv
from pymongo import MongoClient
from pymongo.database import Database
from pymongo.errors import ConfigurationError, ConnectionFailure, PyMongoError

# Cargar variables de entorno de forma segura desde la raíz del proyecto
ruta_env = Path(__file__).resolve().parent.parent / ".env"
load_dotenv(dotenv_path=ruta_env)

# Variables globales para el manejo del Pool de Conexiones
_cliente_mongo: Optional[MongoClient] = None


def obtener_conexion_db() -> Optional[Database]:
    global _cliente_mongo

    user = os.getenv("MONGO_ROOT_USERNAME")
    password = os.getenv("MONGO_ROOT_PASSWORD")
    db_name = os.getenv("MONGO_DATABASE", "comerciotech_db")

    # Configuración de Pooling y Resiliencia
    max_pool = int(os.getenv("MONGO_MAX_POOL_SIZE", "50"))
    min_pool = int(os.getenv("MONGO_MIN_POOL_SIZE", "10"))
    timeout_ms = int(os.getenv("MONGO_TIMEOUT_MS", "5000"))
    usar_tls = os.getenv("MONGO_USE_TLS", "false").lower() == "true"

    uri_defecto = f"mongodb://{user}:{password}@localhost:27018/?authSource=admin"
    mongo_uri = os.getenv("MONGO_URI", uri_defecto)

    # Si ya existe un cliente activo, se reutiliza (Singleton + Pooling)
    if _cliente_mongo is not None:
        try:
            # Validar que la conexión sigue activa (ping ligero)
            _cliente_mongo.admin.command("ping")
            return _cliente_mongo[db_name]
        except PyMongoError:
            # Si el pool cayó, forzamos la reconexión
            _cliente_mongo = None

    try:
        # Inicializar conexión segura con parámetros avanzados
        _cliente_mongo = MongoClient(
            mongo_uri,
            serverSelectionTimeoutMS=timeout_ms,
            connectTimeoutMS=timeout_ms,
            maxPoolSize=max_pool,
            minPoolSize=min_pool,
            tls=usar_tls,
            # tlsAllowInvalidCertificates=True  # Habilitar en desarrollo si se usa TLS autorealizado
        )

        # Validar conexión real al cluster/servidor
        _cliente_mongo.admin.command("ping")
        print(
            f"[Conexión Exitosa] Conectado a MongoDB. Pool configurado: {min_pool}-{max_pool} conexiones."
        )

        return _cliente_mongo[db_name]

    except ConnectionFailure as e:
        print(
            f"(Error Crítico de Conexión) El servidor MongoDB no responde.\n"
            f"Host objetivo: {mongo_uri.split('@')[-1]}\nDetalle: {e}",
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
