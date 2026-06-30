import os
import sys
from pathlib import Path

from dotenv import load_dotenv
from pymongo import MongoClient
from pymongo.errors import ConfigurationError, ConnectionFailure

ruta_env = Path(__file__).resolve().parent.parent / ".env"
load_dotenv(dotenv_path=ruta_env)


def obtener_conexion_db():
    user = os.getenv("MONGO_ROOT_USERNAME")
    password = os.getenv("MONGO_ROOT_PASSWORD")
    db_name = os.getenv("MONGO_DATABASE", "comerciotech_db")

    uri_defecto = f"mongodb://{user}:{password}@localhost:27018/?authSource=admin"
    mongo_uri = os.getenv("MONGO_URI", uri_defecto)

    try:
        client = MongoClient(
            mongo_uri, serverSelectionTimeoutMS=5000, connectTimeoutMS=5000
        )
        client.admin.command("ping")
        return client[db_name]

    except (ConnectionFailure, ConfigurationError) as e:
        print(
            f"(Error Crítico NoSQL): Error de comunicación. URI utilizada: {mongo_uri.split('@')[-1]}. Detalle: {e}",
            file=sys.stderr,
        )
        sys.exit(1)
