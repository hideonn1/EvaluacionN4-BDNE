from views.vista_base import VistaBase


class VistaProducto(VistaBase):
    def menu(self) -> str:
        self.mostrar_titulo("GESTIÓN DE PRODUCTOS")
        return self.pedir_opcion(
            {
                "1": "Registrar producto",
                "2": "Listar productos en stock",
                "3": "Eliminar producto",
                "0": "Volver",
            }
        )

    def solicitar_datos_producto(self) -> dict:
        return {
            "nombre": self.pedir_texto("Nombre del producto"),
            "precio": self.pedir_numero("Precio", tipo=float),
            "stock": int(self.pedir_numero("Stock inicial", tipo=int)),
            "categoria": self.pedir_texto("Categoría (opcional)") or None,
        }

    def solicitar_id(self) -> str:
        return self.pedir_texto("ID del producto (_id de Mongo)")

    def mostrar_producto(self, producto: dict) -> None:
        if not producto:
            self.mostrar_error("Producto no encontrado.")
            return
        print(f"  ID       : {producto.get('_id')}")
        print(f"  Nombre   : {producto.get('nombre')}")
        print(f"  Precio   : ${producto.get('precio')}")
        print(f"  Stock    : {producto.get('stock')} unidades")
        print(f"  Categoría: {producto.get('categoria') or '-'}")

    def mostrar_lista_productos(self, productos: list) -> None:
        if not productos:
            self.mostrar_mensaje("No hay productos disponibles.")
            return
        for p in productos:
            print(
                f"  - [{p.get('_id')}] {p.get('nombre')} "
                f"| stock: {p.get('stock')} | ${p.get('precio')}"
            )

    def solicitar_datos_modificacion_producto(self, actual: dict) -> dict:
        print("\n  (Presione Enter para mantener el valor actual)")
        campos = {}

        nuevo_nombre = self.pedir_texto(f"Nombre [{actual.get('nombre')}]")
        if nuevo_nombre:
            campos["nombre"] = nuevo_nombre

        nueva_categoria = input(
            f"Categoría [{actual.get('categoria') or '-'}]: "
        ).strip()
        if nueva_categoria:
            campos["categoria"] = nueva_categoria

        precio_str = input(f"Precio [${actual.get('precio')}]: ").strip()
        if precio_str:
            while True:
                try:
                    nuevo_precio = float(precio_str)
                    if nuevo_precio <= 0:
                        raise ValueError
                    campos["precio"] = nuevo_precio
                    break
                except ValueError:
                    self.mostrar_error(
                        "El precio debe ser un número mayor a 0. "
                        f"Valor ingresado: '{precio_str}'"
                    )
                    precio_str = input(f"Precio [${actual.get('precio')}]: ").strip()
                    if not precio_str:
                        break

        stock_str = input(f"Stock [{actual.get('stock')} unidades]: ").strip()
        if stock_str:
            while True:
                try:
                    nuevo_stock = int(stock_str)
                    if nuevo_stock <= 0:
                        raise ValueError
                    campos["stock"] = nuevo_stock
                    break
                except ValueError:
                    self.mostrar_error(
                        "El stock debe ser un número entero mayor a 0. "
                        f"Valor ingresado: '{stock_str}'"
                    )
                    stock_str = input(
                        f"Stock [{actual.get('stock')} unidades]: "
                    ).strip()
                    if not stock_str:
                        break

        return campos
