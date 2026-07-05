# SISTEMA COMERCIOTECH

Sistema de gestión de clientes, productos y pedidos para un comercio,
desarrollado como Evaluación 4 del curso **Bases de Datos No
Estructuradas** de INACAP. Aplica **MongoDB** como motor de
base de datos NoSQL documental, contenedores **Docker** para el
entorno de despliegue, y una arquitectura de software en **Python**
organizada bajo el patrón **MVC** con **Programación Orientada a
Objetos**.

## Entorno de despliegue colaborativo

La aplicación CLI se ejecuta finalmente sobre un servidor **Debian GNU/Linux**.
Parte del desarrollo se realizó directamente en la máquina virtual de dicho servidor,
administrada por uno de los integrantes del equipo; el resto del equipo se conectó mediante
una VPN mesh con SSH, configurada con Tailscale, para tareas de CI/CD, desarrollo, instalación
de dependencias y configuración general del servidor.

## Objetivo del proyecto

El proyecto busca demostrar el ciclo completo de diseño e implementación de una
solución de persistencia NoSQL para un caso de negocio, cubriendo:

1. **Análisis de requisitos del negocio**: volúmenes de datos,
   rendimiento, escalabilidad, disponibilidad, seguridad y
   cumplimiento normativo de un comercio que gestiona clientes,
   catálogo de productos y pedidos.
2. **Selección y configuración del entorno**: sistema operativo,
   plataforma de virtualización (contenedores Docker) y los recursos
   asignados a cada servicio.
3. **Instalación y configuración segura de MongoDB**: autenticación
   por usuario/contraseña, restricciones de red, límites de recursos
   y buenas prácticas de hardening (ver `mongod.conf` y
   `docker-compose.yml`).
4. **Seguridad y Control de Acceso Basado en Roles (RBAC)**: Creación
   de múltiples roles en MongoDB (`admin`, `readWrite`, `read`, `clusterMonitor`)
   y autenticación en la aplicación. Los menús de la CLI se ajustan 
   dinámicamente protegiendo las rutas según el rol.
5. **Diseño del modelo de datos NoSQL**: colecciones `clientes`,
   `productos` y `pedidos`, con subdocumentos embebidos para los
   ítems de cada pedido, validación de esquema (`$jsonSchema`) e
   índices (ver `scripts/init-mongo.js`).
6. **Desarrollo de la capa de aplicación**: conexión segura al motor
   de base de datos, funciones CRUD organizadas en
   una arquitectura **Modelo-Vista-Controlador**. Incluye manejo
   robusto de interrupciones del teclado (`CTRL + C`) y validaciones 
   interactivas de stock.

## Arquitectura

```
.
├── Dockerfile               # Imagen de MongoDB (config + copia del script de inicialización)
├── Dockerfile.app           # Imagen de la aplicación Python (dependencias precompiladas)
├── docker-compose.yml       # Orquesta los servicios mongodb y app
├── mongod.conf              # Configuración del servidor MongoDB
├── requirements.txt         # Dependencias Python (pymongo, python-dotenv)
├── requirements-dev.txt     # Dependencias de desarrollo y pruebas (pytest, flake8)
├── pyproject.toml           # Configuración del proyecto Python
├── pytest.ini               # Configuración para pytest
├── .env.example             # Plantilla de variables de entorno (copiar a .env)
├── diagrama_clases.puml     # Diagrama de clases del sistema en PlantUML
├── diagrama_nosql.mmd       # Diagrama NoSQL del sistema en Mermaid
├── src/
│   ├── main.py              # Punto de entrada (modo interactivo y --test-mode)
│   ├── database.py          # Conexión a MongoDB (Singleton + pool de conexiones)
│   ├── controllers/         # CAPA CONTROLADOR
│   │   ├── controlador_cliente.py
│   │   ├── controlador_pedido.py    # Crea pedidos: valida cliente y descuenta stock
│   │   ├── controlador_principal.py # Menú general (compone los 3 controladores)
│   │   └── controlador_producto.py
│   ├── models/              # CAPA MODELO
│   │   ├── base_model.py    # RepositorioBase (ABC): CRUD genérico + manejo de errores
│   │   ├── cliente.py       # Cliente (entidad) + RepositorioClientes
│   │   ├── pedido.py        # Pedido + ItemPedido (subdocumento) + RepositorioPedidos
│   │   └── producto.py      # Producto (entidad) + RepositorioProductos
│   ├── scripts/             # SCRIPTS DE BASE DE DATOS
│   │   └── init-mongo.js    # Crea colecciones con validación de esquema + índices
│   └── views/               # CAPA VISTA
│       ├── vista_base.py    # Utilidades de entrada/salida por consola
│       ├── vista_cliente.py
│       ├── vista_pedido.py
│       └── vista_producto.py
└── tests/                   # CAPA DE PRUEBAS UNITARIAS Y DE INTEGRACIÓN
    ├── conftest.py          # Configuración y fixtures de pytest
    ├── test_database.py     # Pruebas para la conexión a la base de datos
    ├── controllers/
    │   └── test_controlador_principal.py # Pruebas del controlador principal
    └── models/
        └── test_producto.py # Pruebas unitarias para el modelo de productos
```

- **Modelo**: cada colección tiene una entidad (`@dataclass`) y un
  **Repositorio** que hereda de `RepositorioBase`, encapsulando CRUD,
  validación de datos y manejo de `PyMongoError`.
- **Vista**: solo construye menús, solicita datos por consola y
  formatea la salida. No conoce MongoDB ni reglas de negocio.
- **Controlador**: conecta Vista y Modelo. `ControladorPedido`, por
  ejemplo, orquesta tres repositorios a la vez (pedidos, clientes y
  productos) para validar que el cliente exista y descontar stock al
  crear un pedido, revirtiéndolo si la creación falla.

## Requisitos previos

- Docker y Docker Compose instalados.
- Un archivo `.env` en la raíz del proyecto (no se sube al
  repositorio). Cópialo desde la plantilla:

  ```bash
  cp .env.example .env
  ```

  Luego edita `.env` con tus propias credenciales:

  ```
  MONGO_ROOT_USERNAME=tu_usuario
  MONGO_ROOT_PASSWORD=tu_password_segura
  MONGO_DATABASE=comerciotech_db
  APP_USERNAME=app_user
  APP_PASSWORD=app_pass_123
  AUDITOR_USERNAME=auditor_user
  AUDITOR_PASSWORD=auditor_pass_123
  MONITOR_USERNAME=monitor_user
  MONITOR_PASSWORD=monitor_pass_123
  ```

  > ⚠️ Evita caracteres reservados de URI (`$ ? @ : / # & +`) en la
  > contraseña, ya que se usa para construir la cadena de conexión de
  > MongoDB (`MONGO_URI`) directamente en `docker-compose.yml`.

## Cómo levantar el proyecto

```bash
# Construye las imágenes y levanta ambos servicios en segundo plano
docker compose up -d --build mongodb app
```

Esto crea:
- `mongodb_comerciotech`: contenedor de MongoDB, con las colecciones
  y validación de esquema inicializadas por `scripts/init-mongo.js`
  la primera vez que se crea el volumen.
- `app_comerciotech`: contenedor de la aplicación Python, con las
  dependencias ya instaladas en la imagen (`Dockerfile.app`).

## Cómo ejecutar la aplicación (modo interactivo)

```bash
docker compose run --rm app python src/main.py
```

Muestra un login inicial por consola. Una vez autenticado, despliega 
el menú principal (Clientes / Productos / Pedidos / Estado del servidor) 
operando sobre la base de datos y mostrando opciones dinámicamente 
según los privilegios de tu rol. Si deseas abortar cualquier formulario 
o acción, puedes usar `CTRL + C` para volver al menú de forma segura.

## Cómo correr el smoke-test (usado por el pipeline de CI/CD)

Valida la conexión a MongoDB y una consulta básica, sin entrar al
menú interactivo:

```bash
docker compose run --rm app python src/main.py --test-mode
```

Retorna código de salida `0` si la conexión y la consulta fueron
exitosas, o `1` en caso de error (por ejemplo, si MongoDB no está
disponible o las credenciales son inválidas).

## Verificaciones manuales adicionales

**Ver los índices y la validación de esquema aplicados a una colección:**

```bash
docker exec -it mongodb_comerciotech mongosh \
  -u <MONGO_ROOT_USERNAME> -p <MONGO_ROOT_PASSWORD> \
  --authenticationDatabase admin comerciotech_db \
  --eval "db.clientes.getIndexes()"
```

**Probar que el validador de esquema rechaza datos inválidos:**

```bash
docker exec -it mongodb_comerciotech mongosh \
  -u <MONGO_ROOT_USERNAME> -p <MONGO_ROOT_PASSWORD> \
  --authenticationDatabase admin comerciotech_db \
  --eval 'db.clientes.insertOne({rut: "malformado", nombre: "Test", email: "no-es-email"})'
```

Debe fallar con `Document failed validation`.

## Detener y limpiar el entorno

```bash
docker compose down        # detiene y elimina los contenedores
docker compose down -v     # además elimina el volumen de datos de MongoDB
```

> Usa `-v` cuando quieras forzar que `scripts/init-mongo.js` se
> vuelva a ejecutar desde cero (por ejemplo, tras modificar el
> esquema de validación).

## Próximos pasos sugeridos

- Agregar pruebas unitarias por repositorio (mockeando
  `pymongo.collection.Collection` o usando `mongomock`).
- Agregar reportes agregados (ej. ventas por producto) usando el
  framework de agregación de MongoDB.
