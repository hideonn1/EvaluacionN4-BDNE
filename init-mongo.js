db = db.getSiblingDB(process.env.MONGO_INITDB_DATABASE || "comerciotech_db");

db.createCollection("clientes");
db.createCollection("productos");
db.createCollection("pedidos");

db.clientes.createIndex({ rut: 1 }, { unique: true });
db.productos.createIndex({ nombre: 1 });
db.pedidos.createIndex({ codigo_pedido: 1 }, { unique: true });

print("init-mongo.js ejecutado: colecciones e índices creados.");
