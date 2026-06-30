# SISTEMA COMERCIOTECH — Arquitectura MVC

Refactorización del proyecto original (`database.py` + `crud.py` + `main.py`)
a una arquitectura **Modelo-Vista-Controlador**, aplicando Programación
Orientada a Objetos en cada capa.

## Estructura

```
src/
├── main.py                          # Punto de entrada (modo interactivo y --test-mode)
├── database.py                      # Infraestructura: conexión a MongoDB
├── models/                          # CAPA MODELO
│   ├── base_model.py                #   RepositorioBase (ABC): CRUD genérico + manejo de errores
│   ├── cliente.py                   #   Cliente (entidad) + RepositorioClientes
│   ├── producto.py                  #   Producto (entidad) + RepositorioProductos
│   └── pedido.py                    #   Pedido + ItemPedido (subdocumento) + RepositorioPedidos
├── views/                           # CAPA VISTA
│   ├── vista_base.py                #   VistaBase: utilidades de E/S por consola
│   ├── vista_cliente.py
│   ├── vista_producto.py
│   └── vista_pedido.py
└── controllers/                     # CAPA CONTROLADOR
    ├── controlador_cliente.py
    ├── controlador_producto.py
    ├── controlador_pedido.py
    └── controlador_principal.py     # Orquesta el menú general (compone los 3 controladores)
```

## Por qué esta organización

- **Modelo** (`models/`): cada colección de MongoDB tiene una entidad
  (`@dataclass`) que representa el documento en memoria, y un
  **Repositorio** que hereda de `RepositorioBase` (clase abstracta) y
  encapsula las operaciones CRUD, la validación de datos y el manejo
  de errores de `PyMongoError`. Esto evita duplicar `try/except`
  como ocurría en el `crud.py` original y aplica el patrón
  *Repository* clásico sobre PyMongo.
- **Vista** (`views/`): solo construye menús, pide datos por consola
  y formatea la salida. No conoce MongoDB ni reglas de negocio.
- **Controlador** (`controllers/`): conecta Vista y Modelo. Decide
  qué hacer con la entrada del usuario, construye las entidades y
  llama al repositorio correspondiente, sin mezclar lógica de
  presentación ni de persistencia.

## Cambios relevantes respecto al proyecto original

- `crud.py` se reemplaza por los repositorios dentro de `models/`
  (misma responsabilidad, pero con clases, herencia y validación).
- Se agregó **validación de datos** antes de insertar (formato de
  RUT y email, precio/stock no negativos, estados de pedido válidos).
- `pedido.py` modela explícitamente **subdocumentos** (`ItemPedido`)
  embebidos dentro de cada pedido, con cálculo de `subtotal` y
  `total`.
- `obtener_pedidos_activos` ahora filtra realmente por `estado` (no
  entregado/cancelado), en vez de devolver todos los documentos.
- `main.py` conserva exactamente el comportamiento de
  `--test-mode` que usa el pipeline de CI/CD (`docker-compose.yml`),
  por lo que **no es necesario modificar** `Dockerfile`,
  `docker-compose.yml` ni `requirements.txt`.

## Ejecución

```bash
# Entorno interactivo
python src/main.py

# Smoke-test (usado por CI/CD)
python src/main.py --test-mode
```

## Cambios en la siguiente actualización:

- Agregar pruebas unitarias por repositorio (mockeando `pymongo.collection.Collection`).
- Extender `ControladorPedido` con una acción para **crear** pedidos
  (seleccionando cliente y productos desde los otros repositorios),
  dejado fuera de este alcance para no acoplar controladores entre sí.
