import os
import sys
 
from App import logic
from DataStructures.List import array_list as lt
 
# Límite de recursión (recomendado en el enunciado para evitar RecursionError)
default_limit = 1000
sys.setrecursionlimit(default_limit * 10)
 
DATA_FILES = {
    "1": "chocolate_sale_100_elementos.csv",
    "2": "chocolate_sale_20_pct.csv",
    "3": "chocolate_sale_40_pct.csv",
    "4": "chocolate_sale_60_pct.csv",
    "5": "chocolate_sale_80_pct.csv",
    "6": "chocolate_sale_100_pct.csv",
}
 
 
# ---------------------------------------------------------------------------
# Utilidades de entrada y de impresión
# ---------------------------------------------------------------------------
 
def data_path(filename):
    """
    Busca el archivo en Data/Datos (relativa a este archivo, sin rutas absolutas).
    """
    base = os.path.dirname(os.path.abspath(__file__))
    for folder in ("Data", "data"):
        for root in (os.path.join(base, ".."), base):
            path = os.path.join(root, folder, "Datos", filename)
            if os.path.exists(path):
                return path
    return os.path.join(base, "..", "Data", "Datos", filename)
 
 
def ask_int(message):
    while True:
        try:
            return int(input(message).strip())
        except ValueError:
            print("Valor inválido, intente de nuevo.")
 
 
def ask_float(message):
    while True:
        try:
            return float(input(message).strip())
        except ValueError:
            print("Valor inválido, intente de nuevo.")
 
 
def ask_text(message):
    return input(message).strip()
 
 
def ask_date(message):
    while True:
        text = input(message).strip()
        if len(text) == 10 and text[4] == "-" and text[7] == "-":
            return text
        print("Formato inválido, use YYYY-MM-DD.")
 
 
def money(value):
    return "{:,.2f}".format(value)
 
 
def ms(value):
    return "{:.3f} ms".format(value)
 
 
def print_table(rows, columns, split_at=None):
    """
    Imprime una array_list de diccionarios como tabla.
    columns: lista de (encabezado, llave, formato o None).
    split_at: si se da, inserta una línea '...' después de esa cantidad de filas.
    """
    data = lt.to_py_list(rows)
    if len(data) == 0:
        print("  (sin pedidos para mostrar)")
        return
 
    table = []
    for row in data:
        line = []
        for _, key, fmt in columns:
            line.append(fmt(row[key]) if fmt else str(row[key]))
        table.append(line)
 
    widths = []
    for c in range(len(columns)):
        w = len(columns[c][0])
        for line in table:
            if len(line[c]) > w:
                w = len(line[c])
        widths.append(w)
 
    header = " | ".join(columns[c][0].ljust(widths[c]) for c in range(len(columns)))
    print(header)
    print("-" * len(header))
    for i in range(len(table)):
        if split_at is not None and i == split_at:
            print("...".center(len(header)))
        print(" | ".join(table[i][c].ljust(widths[c]) for c in range(len(columns))))
 
 
def one_row(order):
    rows = lt.new_list()
    lt.add_last(rows, order)
    return rows
 
 
# Columnas reutilizadas
COLS_LOAD = [
    ("Order_ID", "Order_ID", None), ("Product", "Product", None),
    ("Country", "Country", None), ("Channel", "Channel", None),
    ("Order_Date", "Order_Date", None), ("Boxes_Shipped", "Boxes_Shipped", None),
    ("Price_per_Box", "Price_per_Box", money), ("Amount", "Amount", money),
]
COLS_REQ_1 = [
    ("Order_ID", "Order_ID", None), ("Product", "Product", None),
    ("Country", "Country", None), ("Channel", "Channel", None),
    ("Order_Date", "Order_Date", None), ("Discount_Pct", "Discount_Pct", None),
    ("Price_per_Box", "Price_per_Box", money),
    ("Boxes_Shipped", "Boxes_Shipped", None), ("Amount", "Amount", money),
]
COLS_REQ_2 = [
    ("Order_ID", "Order_ID", None), ("Product", "Product", None),
    ("Channel", "Channel", None), ("Order_Date", "Order_Date", None),
    ("Boxes_Shipped", "Boxes_Shipped", None),
    ("Price_per_Box", "Price_per_Box", money),
    ("Marketing_Spend", "Marketing_Spend", money), ("Amount", "Amount", money),
]
COLS_REQ_3 = [
    ("Order_ID", "Order_ID", None), ("Product", "Product", None),
    ("Country", "Country", None), ("Order_Date", "Order_Date", None),
    ("Marketing_Spend", "Marketing_Spend", money),
    ("Boxes_Shipped", "Boxes_Shipped", None),
    ("Amount (Costo total)", "Amount", money),
    ("Aporte comercial", "Aporte_Comercial", money),
]
COLS_REQ_4 = [
    ("Order_ID", "Order_ID", None), ("Channel", "Channel", None),
    ("Order_Date", "Order_Date", None),
    ("Boxes_Shipped", "Boxes_Shipped", None), ("Amount", "Amount", money),
]
COLS_REQ_5 = [
    ("Product", "Product", None), ("Pedidos", "orders", None),
    ("Total Boxes_Shipped", "boxes", None),
    ("Recaudo total", "revenue", money),
    ("Price_per_Box prom.", "avg_price_per_box", money),
    ("Discount_Pct prom.", "avg_discount_pct", money),
    ("Marketing_Spend total", "marketing", money),
]
COLS_REQ_6 = [
    ("Country", "Country", None), ("Pedidos", "orders", None),
    ("Amount total", "amount", money),
    ("Marketing_Spend total", "marketing", money),
    ("Boxes_Shipped total", "boxes", None),
    ("Price_per_Box prom.", "avg_price_per_box", money),
    ("Eficiencia de mercadeo", "efficiency", "{:.4f}".format),
]
 
 
# ---------------------------------------------------------------------------
# Vista
# ---------------------------------------------------------------------------
 
def new_logic():
    """
        Se crea una instancia del controlador
    """
    return logic.new_logic()
 
 
def print_menu():
    print("Bienvenido")
    print("0- Cargar información")
    print("1- Ejecutar Requerimiento 1")
    print("2- Ejecutar Requerimiento 2")
    print("3- Ejecutar Requerimiento 3")
    print("4- Ejecutar Requerimiento 4")
    print("5- Ejecutar Requerimiento 5")
    print("6- Ejecutar Requerimiento 6")
    print("7- Salir")
 
 
def load_data(control):
    """
    Carga los datos y muestra el reporte de carga
    """
    print("Archivos disponibles:")
    for key in DATA_FILES:
        print("  " + key + "- " + DATA_FILES[key])
    option = input("Seleccione el archivo a cargar: ").strip()
    if option not in DATA_FILES:
        print("Opción de archivo inválida.\n")
        return False
 
    path = data_path(DATA_FILES[option])
    if not os.path.exists(path):
        print("No se encontró el archivo " + DATA_FILES[option] + " en la carpeta Data/Datos.\n")
        return False
 
    print("Cargando información de los archivos ....\n")
    report = logic.load_data(control, path)
 
    print("Tiempo de carga: " + ms(report["time_ms"]))
    print("Total de pedidos cargados: " + str(report["total_orders"]))
    print("\nPedidos por canal de venta:")
    print_table(report["orders_by_channel"],
                [("Channel", "Channel", None), ("Pedidos", "count", None)])
    print("\nFecha más antigua: " + str(report["oldest_date"]))
    print("Fecha más reciente: " + str(report["newest_date"]))
 
    print("\nPedido con menor Amount:")
    print_table(one_row(report["min_amount_order"]), COLS_LOAD)
    print("\nPedido con mayor Amount:")
    print_table(one_row(report["max_amount_order"]), COLS_LOAD)
 
    print("\nPrimeros 5 pedidos (orden descendente por Amount):")
    print_table(report["first_5"], COLS_LOAD)
    print("\nÚltimos 5 pedidos (orden descendente por Amount):")
    print_table(report["last_5"], COLS_LOAD)
    print()
    return True
 
 
def print_req_1(control):
    """
        Función que imprime la solución del Requerimiento 1 en consola
    """
    year = ask_int("Año del pedido (YYYY): ")
    month = ask_int("Mes del pedido (1-12): ")
    min_d = ask_float("Descuento mínimo (%): ")
    max_d = ask_float("Descuento máximo (%): ")
 
    r = logic.req_1(control, year, month, min_d, max_d)
 
    print("\nTiempo de ejecución: " + ms(r["time_ms"]))
    print("Pedidos que cumplen el filtro: " + str(r["count"]))
    print("Monto total recaudado: " + money(r["total_amount"]))
    print("Promedio de Price_per_Box: " + money(r["avg_price_per_box"]))
    print("Promedio de Boxes_Shipped: " + money(r["avg_boxes_shipped"]))
    if r["count"] > 20:
        print("\n(Se muestran los primeros 10 y los últimos 10 pedidos)")
    print()
    print_table(r["orders"], COLS_REQ_1, 10 if r["count"] > 20 else None)
    print()


def print_req_2(control):
    """
    Función que imprime la solución del Requerimiento 2 en consola
    """
    country = ask_text("País (Country): ")
    min_boxes = ask_int("Número mínimo de cajas enviadas: ")
    max_boxes = ask_int("Número máximo de cajas enviadas: ")

    r = logic.req_2(control, country, min_boxes, max_boxes)

    print("\nTiempo de ejecución: " + ms(r["time_ms"]))
    print("Pedidos que cumplen el filtro: " + str(r["count"]))
    print("Productos diferentes encontrados: " + str(r["distinct_products"]))
    print("Promedio de Marketing_Spend: " + money(r["avg_marketing_spend"]))
    print("Promedio de Amount: " + money(r["avg_amount"]))
    print(f"Producto más frecuente: {r['most_frequent_product']} (Pedidos: {r['most_frequent_product_count']})")
    
    if r["count"] > 20:
        print("\n(Se muestran los primeros 10 y los últimos 10 pedidos)")
    print()
    print_table(r["orders"], COLS_REQ_2, 10 if r["count"] > 20 else None)
    print()


def print_req_3(control):
    """
        Función que imprime la solución del Requerimiento 3 en consola
    """
    # TODO: Imprimir el resultado del requerimiento 3
    pass


def print_req_4(control):
    """
    Función que imprime la solución del Requerimiento 4 en consola
    """
    product = ask_text("Producto (Product): ")
    country = ask_text("País (Country): ")

    r = logic.req_4(control, product, country)

    print("\nTiempo de ejecución: " + ms(r["time_ms"]))
    print("Pedidos que cumplen el filtro: " + str(r["count"]))
    print("Precio promedio de Price_per_Box: " + money(r["avg_price_per_box"]))
    print("Promedio de Discount Pct: " + str(r["avg_discount_pct"]) + "%")
    print("Promedio de Marketing_Spend: " + money(r["avg_marketing_spend"]))
    print("Promedio de Boxes_Shipped: " + str(r["avg_boxes_shipped"]))
    print()
    print_table(r["top"], COLS_REQ_4)
    print()


def print_req_5(control):
    """
        Función que imprime la solución del Requerimiento 5 en consola
    """
    n = ask_int("Número N de productos: ")
    country = ask_text("País (Country): ")
    start = ask_date("Fecha inicial (YYYY-MM-DD): ")
    end = ask_date("Fecha final (YYYY-MM-DD): ")
 
    r = logic.req_5(control, n, country, start, end)
 
    print("\nTiempo de ejecución: " + ms(r["time_ms"]))
    print("Pedidos que cumplen el filtro: " + str(r["total_orders"]))
    print("Productos diferentes encontrados: " + str(r["distinct_products"]))
    print("Recaudo total: " + money(r["total_amount"]))
    print()
    print_table(r["top"], COLS_REQ_5)
    print()
 
 
def print_req_6(control):
    """
        Función que imprime la solución del Requerimiento 6 en consola
    """
    n = ask_int("Número N de países: ")
    product = ask_text("Producto (Product): ")
    start = ask_date("Fecha inicial (YYYY-MM-DD): ")
    end = ask_date("Fecha final (YYYY-MM-DD): ")
 
    r = logic.req_6(control, n, product, start, end)
 
    print("\nTiempo de ejecución: " + ms(r["time_ms"]))
    print("Pedidos que cumplen el filtro: " + str(r["total_orders"]))
    print("Países diferentes encontrados: " + str(r["distinct_countries"]))
    print("Amount total: " + money(r["total_amount"]))
    print("Marketing_Spend total: " + money(r["total_marketing"]))
    print()
    print_table(r["top"], COLS_REQ_6)
    print()
 
 
# main del ejercicio
def main():
    """
    Menu principal
    """
    control = new_logic()
    loaded = False
    working = True
    # ciclo del menu
    while working:
        print_menu()
        inputs = input('Seleccione una opción para continuar\n').strip()
        if not inputs.isdigit():
            print("Opción errónea, vuelva a elegir.\n")
            continue
        option = int(inputs)
 
        if option == 0:
            control = new_logic()  # evita duplicar datos si se carga dos veces
            loaded = load_data(control)
        elif 1 <= option <= 6:
            if not loaded:
                print("Primero debe cargar la información (opción 0).\n")
            elif option == 1:
                print_req_1(control)
            elif option == 2:
                print_req_2(control)
            elif option == 3:
                print_req_3(control)
            elif option == 4:
                print_req_4(control)
            elif option == 5:
                print_req_5(control)
            else:
                print_req_6(control)
        elif option == 7:
            working = False
            print("\nGracias por utilizar el programa")
        else:
            print("Opción errónea, vuelva a elegir.\n")
    sys.exit(0)
 
 
if __name__ == "__main__":
    main()