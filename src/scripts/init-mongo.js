// ============================================================================
// CT-09: Inicialización del esquema y validación de colecciones (Cristóbal)
// 
// El diseño de la base de datos se basa en un modelo documental optimizado 
// para las consultas frecuentes del caso de estudio. Se implementó una capa 
// de validación en el servidor de MongoDB para asegurar la integridad de los 
// datos en tiempo de escritura. 
// 
// Se utiliza el operador $jsonSchema para aplicar restricciones de tipos, 
// formatos obligatorios y rangos de valores, evitando la "contaminación" de 
// la base de datos con documentos mal formados.
// ============================================================================

// Seleccionar la base de datos
db = db.getSiblingDB('comerciotech_db');

// ----------------------------------------------------------------------------
// 1. Colección: clientes
// Basado en src/models/cliente.py
// ----------------------------------------------------------------------------
print("Creando colección 'clientes' con validación de esquema...");
db.createCollection("clientes", {
   validator: {
      $jsonSchema: {
         bsonType: "object",
         required: ["rut", "nombre", "email"],
         properties: {
            rut: {
               bsonType: "string",
               pattern: "^\\d{7,8}-[\\dkK]$",
               description: "RUT del cliente (requerido, formato válido chileno sin puntos)"
            },
            nombre: {
               bsonType: "string",
               description: "Nombre del cliente (requerido)"
            },
            email: {
               bsonType: "string",
               pattern: "^[^@\\s]+@[^@\\s]+\\.[^@\\s]+$",
               description: "Correo electrónico (requerido, formato válido)"
            },
            telefono: {
               bsonType: ["string", "null"],
               description: "Teléfono de contacto (opcional)"
            },
            direccion: {
               bsonType: ["string", "null"],
               description: "Dirección principal del cliente (opcional)"
            }
         }
      }
   },
   validationLevel: "strict",
   validationAction: "error"
});

// Índices para clientes
db.clientes.createIndex({ "rut": 1 }, { unique: true, name: "idx_rut_unique" });
db.clientes.createIndex({ "email": 1 }, { unique: true, name: "idx_email_unique" });

// ----------------------------------------------------------------------------
// 2. Colección: productos
// Basado en src/models/producto.py
// ----------------------------------------------------------------------------
print("Creando colección 'productos' con validación de esquema...");
db.createCollection("productos", {
   validator: {
      $jsonSchema: {
         bsonType: "object",
         required: ["nombre", "precio", "stock"],
         properties: {
            nombre: {
               bsonType: "string",
               description: "Nombre del producto (requerido)"
            },
            precio: {
               bsonType: ["double", "decimal", "int"],
               exclusiveMinimum: 0,
               description: "Precio del producto (requerido, estrictamente mayor a 0)"
            },
            stock: {
               bsonType: ["int", "long"],
               minimum: 0,
               description: "Stock disponible (requerido, mayor o igual a 0)"
            },
            categoria: {
               bsonType: ["string", "null"],
               description: "Categoría del producto (opcional)"
            }
         }
      }
   },
   validationLevel: "strict",
   validationAction: "error"
});

// Índices para productos
db.productos.createIndex({ "nombre": 1 }, { name: "idx_nombre" });
db.productos.createIndex({ "stock": 1 }, { name: "idx_stock" });

// ----------------------------------------------------------------------------
// 3. Colección: pedidos
// Basado en src/models/pedido.py
// ----------------------------------------------------------------------------
print("Creando colección 'pedidos' con validación de esquema...");
db.createCollection("pedidos", {
   validator: {
      $jsonSchema: {
         bsonType: "object",
         required: ["codigo_pedido", "rut_cliente", "items", "estado", "fecha_creacion", "total"],
         properties: {
            codigo_pedido: {
               bsonType: "string",
               description: "Código único de identificación del pedido (requerido)"
            },
            rut_cliente: {
               bsonType: "string",
               description: "RUT del cliente asociado (requerido, referencia lógica a clientes)"
            },
            items: {
               bsonType: "array",
               minItems: 1,
               description: "Arreglo de productos incluidos en el pedido (requerido, al menos 1)",
               items: {
                  bsonType: "object",
                  required: ["producto_id", "nombre_producto", "cantidad", "precio_unitario", "subtotal"],
                  properties: {
                     producto_id: {
                        bsonType: "string",
                        description: "ID del producto (como string)"
                     },
                     nombre_producto: {
                        bsonType: "string",
                        description: "Nombre del producto"
                     },
                     cantidad: {
                        bsonType: "int",
                        minimum: 1,
                        description: "Cantidad solicitada (mínimo 1)"
                     },
                     precio_unitario: {
                        bsonType: ["double", "decimal", "int"],
                        minimum: 0,
                        description: "Precio unitario del producto al momento del pedido"
                     },
                     subtotal: {
                        bsonType: ["double", "decimal", "int"],
                        minimum: 0,
                        description: "Subtotal de este ítem (cantidad * precio_unitario)"
                     }
                  }
               }
            },
            total: {
               bsonType: ["double", "decimal", "int"],
               minimum: 0,
               description: "Monto total calculado del pedido (requerido)"
            },
            estado: {
               enum: ["pendiente", "procesando", "enviado", "entregado", "cancelado"],
               description: "Estado operativo actual del pedido (requerido)"
            },
            fecha_creacion: {
               bsonType: "date",
               description: "Fecha en la que se generó el pedido (requerido)"
            }
         }
      }
   },
   validationLevel: "strict",
   validationAction: "error"
});

// Índices para pedidos
db.pedidos.createIndex({ "codigo_pedido": 1 }, { unique: true, name: "idx_codigo_pedido_unique" });
db.pedidos.createIndex({ "rut_cliente": 1 }, { name: "idx_rut_cliente" });
db.pedidos.createIndex({ "estado": 1 }, { name: "idx_estado" });



print("Inicialización y validación completada exitosamente.");