import csv
import time
 
from DataStructures.List import array_list as lt
from DataStructures.Map import map_linear_probing as lp
from DataStructures.Map import map_separate_chaining as sc
 
csv.field_size_limit(2147483647)
 
 
# ---------------------------------------------------------------------------
# Creación del catálogo
# ---------------------------------------------------------------------------
 
def new_logic():
    """
    Crea el catálogo con las estructuras de datos del reto.
 
    Tablas de hash construidas durante la carga:
 
    * orders          (array_list): todos los pedidos, en el orden del archivo.
    * by_month        (Linear Probing):    "YYYY-MM"          -> array_list de pedidos  (Req 1)
    * by_country      (Linear Probing):    country            -> array_list de pedidos  (Req 2, 5)
    * by_date         (Separate Chaining): "YYYY-MM-DD"       -> array_list de pedidos  (Req 3)
    * by_prod_country (Linear Probing):    "product|country"  -> array_list de pedidos  (Req 4)
    * by_product      (Linear Probing):    product            -> array_list de pedidos  (Req 6)
    * channels        (Separate Chaining): channel            -> número de pedidos      (carga)
 
    Linear Probing se usa donde el número de llaves distintas es pequeño y
    conocido (meses, países, productos): con factor de carga <= 0.5 las
    búsquedas son O(1) con muy buena localidad. Separate Chaining se usa donde
    el número de llaves es grande o impredecible (fechas): los buckets absorben
    las colisiones sin degradar por agrupamiento (clustering).
    """
    catalog = {
        "orders": lt.new_list(),
        "by_month": lp.new_map(100, 0.5),
        "by_country": lp.new_map(100, 0.5),
        "by_date": sc.new_map(1000, 4),
        "by_prod_country": lp.new_map(1000, 0.5),
        "by_product": lp.new_map(100, 0.5),
        "channels": sc.new_map(10, 4),
    }
    return catalog
 
 
# ---------------------------------------------------------------------------
# Utilidades de parseo
# ---------------------------------------------------------------------------
 
def _to_float(text):
    clean = str(text).strip().replace("$", "").replace("%", "").replace(",", "")
    return float(clean) if clean != "" else 0.0
 
 
def _to_int(text):
    return int(round(_to_float(text)))
 
 
def _to_id(text):
    text = str(text).strip()
    return int(text) if text.isdigit() else text
 
 
def _build_order(row):
    return {
        "Order_ID": _to_id(row["Order_ID"]),
        "Product": row["Product"].strip(),
        "Country": row["Country"].strip(),
        "Channel": row["Channel"].strip(),
        "Order_Date": row["Order_Date"].strip(),
        "Discount_Pct": _to_float(row["Discount_Pct"]),
        "Price_per_Box": _to_float(row["Price_per_Box"]),
        "Marketing_Spend": _to_float(row["Marketing_Spend"]),
        "Boxes_Shipped": _to_int(row["Boxes_Shipped"]),
        "Amount": _to_float(row["Amount"]),
    }
 
 
def _append_lp(table, key, order):
    bucket = lp.get(table, key)
    if bucket is None:
        bucket = lt.new_list()
        lp.put(table, key, bucket)
    lt.add_last(bucket, order)
 
 
def _append_sc(table, key, order):
    bucket = sc.get(table, key)
    if bucket is None:
        bucket = lt.new_list()
        sc.put(table, key, bucket)
    lt.add_last(bucket, order)
 
 
def _first_last(sorted_list, limit=10):
    """
    Si la lista tiene más de 2*limit elementos retorna los primeros `limit` y
    los últimos `limit`; de lo contrario retorna todos.
    """
    total = lt.size(sorted_list)
    result = lt.new_list()
    if total > 2 * limit:
        for i in range(limit):
            lt.add_last(result, lt.get_element(sorted_list, i))
        for i in range(total - limit, total):
            lt.add_last(result, lt.get_element(sorted_list, i))
    else:
        for i in range(total):
            lt.add_last(result, lt.get_element(sorted_list, i))
    return result
 
 
def _safe_div(a, b):
    return a / b if b else 0.0
 
 
# ---------------------------------------------------------------------------
# Criterios de ordenamiento (True si a debe ir antes que b)
# ---------------------------------------------------------------------------
 
def _crit_amount_desc_id_asc(a, b):
    if a["Amount"] != b["Amount"]:
        return a["Amount"] > b["Amount"]
    return a["Order_ID"] < b["Order_ID"]
 
 
def _crit_req1(a, b):
    if a["Discount_Pct"] != b["Discount_Pct"]:
        return a["Discount_Pct"] > b["Discount_Pct"]
    return _crit_amount_desc_id_asc(a, b)
 
 
def _crit_req2(a, b):
    if a["Boxes_Shipped"] != b["Boxes_Shipped"]:
        return a["Boxes_Shipped"] < b["Boxes_Shipped"]
    if a["Order_Date"] != b["Order_Date"]:
        return a["Order_Date"] > b["Order_Date"]
    return a["Order_ID"] < b["Order_ID"]
 
 
def _crit_req3(a, b):
    if a["Amount"] != b["Amount"]:
        return a["Amount"] > b["Amount"]
    aporte_a = a["Amount"] - a["Marketing_Spend"]
    aporte_b = b["Amount"] - b["Marketing_Spend"]
    if aporte_a != aporte_b:
        return aporte_a > aporte_b
    return a["Order_ID"] < b["Order_ID"]
 
 
def _crit_req4(a, b):
    if a["Amount"] != b["Amount"]:
        return a["Amount"] > b["Amount"]
    if a["Marketing_Spend"] != b["Marketing_Spend"]:
        return a["Marketing_Spend"] < b["Marketing_Spend"]
    return a["Order_ID"] < b["Order_ID"]
 
 
def _crit_req5(a, b):
    if a["revenue"] != b["revenue"]:
        return a["revenue"] > b["revenue"]
    if a["boxes"] != b["boxes"]:
        return a["boxes"] > b["boxes"]
    return a["Product"] < b["Product"]
 
 
def _crit_req6(a, b):
    if a["efficiency"] != b["efficiency"]:
        return a["efficiency"] > b["efficiency"]
    if a["amount"] != b["amount"]:
        return a["amount"] > b["amount"]
    return a["Country"] < b["Country"]
 
 
# ---------------------------------------------------------------------------
# Carga de datos
# ---------------------------------------------------------------------------
 
def load_data(catalog, filename):
    """
    Carga los datos del reto leyendo el CSV UNA sola vez y construyendo en la
    misma pasada todas las tablas de hash del catálogo.
 
    Complejidad: O(n) (inserción O(1) amortizado por tabla y por pedido).
    El resumen (primeros/últimos 5 por Amount) usa merge sort: O(n log n).
 
    Retorna un diccionario con el reporte de carga. El tiempo reportado
    ("time_ms") corresponde a la lectura y construcción de las estructuras.
    """
    start = get_time()
 
    channels = catalog["channels"]
    min_date = None
    max_date = None
    min_order = None
    max_order = None
 
    with open(filename, encoding="utf-8-sig", newline="") as f:
        reader = csv.DictReader(f)
        for row in reader:
            order = _build_order(row)
            lt.add_last(catalog["orders"], order)
 
            date = order["Order_Date"]
            _append_lp(catalog["by_month"], date[:7], order)
            _append_sc(catalog["by_date"], date, order)
            _append_lp(catalog["by_country"], order["Country"], order)
            _append_lp(catalog["by_product"], order["Product"], order)
            _append_lp(catalog["by_prod_country"],
                       order["Product"] + "|" + order["Country"], order)
 
            count = sc.get(channels, order["Channel"])
            sc.put(channels, order["Channel"], 1 if count is None else count + 1)
 
            if min_date is None or date < min_date:
                min_date = date
            if max_date is None or date > max_date:
                max_date = date
            if min_order is None or _crit_amount_desc_id_asc(min_order, order):
                min_order = order
            if max_order is None or _crit_amount_desc_id_asc(order, max_order):
                max_order = order
 
    end = get_time()
 
    total = lt.size(catalog["orders"])
    channel_counts = lt.new_list()
    keys = sc.key_set(channels)
    for i in range(lt.size(keys)):
        ch = lt.get_element(keys, i)
        lt.add_last(channel_counts, {"Channel": ch, "count": sc.get(channels, ch)})
 
    first5 = lt.new_list()
    last5 = lt.new_list()
    if total > 0:
        ordered = lt.sub_list(catalog["orders"], 0, total)  # copia: no altera la carga
        lt.merge_sort(ordered, _crit_amount_desc_id_asc)
        for i in range(min(5, total)):
            lt.add_last(first5, lt.get_element(ordered, i))
        for i in range(max(0, total - 5), total):
            lt.add_last(last5, lt.get_element(ordered, i))
 
    return {
        "time_ms": delta_time(start, end),
        "total_orders": total,
        "orders_by_channel": channel_counts,
        "oldest_date": min_date,
        "newest_date": max_date,
        "min_amount_order": min_order,   # menor Amount (desempate: menor Order_ID)
        "max_amount_order": max_order,   # mayor Amount (desempate: menor Order_ID)
        "first_5": first5,
        "last_5": last5,
    }
 
# Funciones de consulta sobre el catálogo


# ---------------------------------------------------------------------------
# Requerimientos
# ---------------------------------------------------------------------------
 
def req_1(catalog, year, month, min_discount, max_discount):
    """
    Req 1: pedidos de un mes y rango de descuento (extremos incluidos).
 
    Hash: by_month (Linear Probing), llave "YYYY-MM" -> acceso O(1) al mes.
    Se recorre solo el bucket del mes (k pedidos), no la lista principal.
    Complejidad: O(1) + O(k) filtrado + O(m log m) merge sort de los m
    pedidos filtrados  =>  O(k + m log m).
    """
    start = get_time()
 
    bucket = lp.get(catalog["by_month"], "%04d-%02d" % (int(year), int(month)))
    filtered = lt.new_list()
    total_amount = 0.0
    sum_price = 0.0
    sum_boxes = 0
    if bucket is not None:
        for i in range(lt.size(bucket)):
            o = lt.get_element(bucket, i)
            if min_discount <= o["Discount_Pct"] <= max_discount:
                lt.add_last(filtered, o)
                total_amount += o["Amount"]
                sum_price += o["Price_per_Box"]
                sum_boxes += o["Boxes_Shipped"]
 
    lt.merge_sort(filtered, _crit_req1)
    count = lt.size(filtered)
    shown = _first_last(filtered)
 
    end = get_time()
    return {
        "time_ms": delta_time(start, end),
        "count": count,
        "total_amount": total_amount,
        "avg_price_per_box": _safe_div(sum_price, count),
        "avg_boxes_shipped": _safe_div(sum_boxes, count),
        "orders": shown,
    }


def req_2(catalog):
    """
    Retorna el resultado del requerimiento 2
    """
    # TODO: Modificar el requerimiento 2
    pass


def req_3(catalog):
    """
    Retorna el resultado del requerimiento 3
    """
    # TODO: Modificar el requerimiento 3
    pass


def req_4(catalog):
    """
    Retorna el resultado del requerimiento 4
    """
    # TODO: Modificar el requerimiento 4
    pass


def req_5(catalog):
    """
    Retorna el resultado del requerimiento 5
    """
    # TODO: Modificar el requerimiento 5
    pass

def req_6(catalog):
    """
    Retorna el resultado del requerimiento 6
    """
    # TODO: Modificar el requerimiento 6
    pass


# Funciones para medir tiempos de ejecucion

def get_time():
    """
    devuelve el instante tiempo de procesamiento en milisegundos
    """
    return float(time.perf_counter()*1000)


def delta_time(start, end):
    """
    devuelve la diferencia entre tiempos de procesamiento muestreados
    """
    elapsed = float(end - start)
    return elapsed
