import os
import pandas as pd

RUTA_CLIENTES = "data/clientes.csv"
RUTA_PRODUCTOS = "data/productos.xlsx"
RUTA_VENTAS = "data/ventas.csv"
RUTA_REPORTE = "reports/reporte_final.xlsx"

# 6.1 CARGA DE INFORMACIÓN
def cargar_datos():
    """
    Carga los tres archivos fuente con Pandas y valida que existan
    y tengan contenido. Retorna una tupla (clientes, productos, ventas).
    """
    for ruta in (RUTA_CLIENTES, RUTA_PRODUCTOS, RUTA_VENTAS):
        if not os.path.exists(ruta):
            raise FileNotFoundError(f"No se encontró el archivo requerido: {ruta}")

    clientes = pd.read_csv(RUTA_CLIENTES, parse_dates=["fecha_registro"])
    productos = pd.read_excel(RUTA_PRODUCTOS)
    ventas = pd.read_csv(RUTA_VENTAS, parse_dates=["fecha"])

    if clientes.empty or productos.empty or ventas.empty:
        raise ValueError("Uno de los archivos fue cargado pero está vacío.")

    print("Carga de información completada:")
    print(f"  clientes.csv  -> {len(clientes)} registros")
    print(f"  productos.xlsx -> {len(productos)} registros")
    print(f"  ventas.csv    -> {len(ventas)} registros")

    return clientes, productos, ventas


def validar_datos(clientes, productos, ventas):
    """
    Valida y limpia la información cargada antes de analizarla:
    - Elimina filas de ventas sin cliente_id (dato crítico faltante).
    - Elimina posibles duplicados exactos en cada DataFrame.
    - Ajusta tipos de datos (astype) para asegurar cálculos correctos.
    """
    ventas = ventas.dropna(subset=["cliente_id"]).copy()
    ventas["cliente_id"] = ventas["cliente_id"].astype(int)

    # drop_duplicates() elimina registros exactamente repetidos, evitando
    # que una venta cargada dos veces infle los indicadores.
    clientes = clientes.drop_duplicates(subset=["cliente_id"])
    productos = productos.drop_duplicates(subset=["producto_id"])
    ventas = ventas.drop_duplicates(subset=["venta_id"])

    return clientes, productos, ventas

# 6.2 EXPLORACIÓN DE DATOS
def explorar_dataframe(df, nombre):
    """
    Muestra la exploración estándar de un DataFrame: cantidad de
    registros, columnas, tipos de datos, primeros/últimos registros
    y cantidad de valores nulos por columna.
    """
    print(f"\n{'=' * 60}")
    print(f"EXPLORACIÓN: {nombre}")
    print("=" * 60)
    print(f"Registros: {len(df)} | Columnas: {df.shape[1]}")
    print(f"Nombres de columnas: {list(df.columns)}")
    print("\nTipos de datos:")
    print(df.dtypes)
    print("\nPrimeros 5 registros:")
    print(df.head(5))
    print("\nÚltimos 5 registros:")
    print(df.tail(5))
    print("\nValores nulos por columna:")
    print(df.isnull().sum())

# 6.3 ANÁLISIS DE VENTAS
def analizar_ventas(ventas):
    """Calcula los indicadores generales de ventas."""
    return {
        "total_ventas": ventas["total_venta"].sum(),
        "promedio_venta": ventas["total_venta"].mean(),
        "venta_maxima": ventas["total_venta"].max(),
        "venta_minima": ventas["total_venta"].min(),
        "num_transacciones": len(ventas),
    }


# 6.4 ANÁLISIS DE CLIENTES
def analizar_clientes(clientes, ventas):
    """
    Calcula indicadores de clientes cruzando ventas con clientes
    mediante merge() (equivalente a un JOIN de SQL).
    """
    # merge() combina ventas con la info de cada cliente usando cliente_id
    # como llave común, algo imposible de hacer directamente solo con ventas.
    ventas_con_cliente = ventas.merge(clientes, on="cliente_id", how="left")

    # groupby() agrupa las ventas por cliente para poder sumar/contar por grupo
    compras_por_cliente = ventas_con_cliente.groupby("cliente_id").agg(
        num_compras=("venta_id", "count"),
        total_gastado=("total_venta", "sum"),
    ).reset_index()

    compras_por_cliente = compras_por_cliente.merge(clientes, on="cliente_id")

    cliente_mas_compras = compras_por_cliente.sort_values(
        "num_compras", ascending=False).iloc[0]
    cliente_mayor_gasto = compras_por_cliente.sort_values(
        "total_gastado", ascending=False).iloc[0]

    # value_counts() cuenta cuántos clientes hay por cada ciudad
    ciudad_top = clientes["ciudad"].value_counts().idxmax()
    clientes_en_ciudad_top = clientes["ciudad"].value_counts().max()

    return {
        "cliente_mas_compras": (cliente_mas_compras["nombre"], int(cliente_mas_compras["num_compras"])),
        "cliente_mayor_gasto": (cliente_mayor_gasto["nombre"], float(cliente_mayor_gasto["total_gastado"])),
        "ciudad_mayor_clientes": (ciudad_top, int(clientes_en_ciudad_top)),
        "promedio_compra_por_cliente": compras_por_cliente["total_gastado"].mean(),
        "compras_por_cliente": compras_por_cliente,
    }


# 6.5 ANÁLISIS DE PRODUCTOS
def analizar_productos(productos, ventas):
    """
    Calcula indicadores de productos: más/menos vendido y mayor/menor
    ingreso, usando groupby() y pivot_table() sobre las ventas.
    """
    ventas_con_producto = ventas.merge(productos, on="producto_id", how="left")

    # pivot_table() resume unidades vendidas e ingresos por producto,
    # similar a una tabla dinámica de Excel.
    resumen_producto = ventas_con_producto.pivot_table(
        index="nombre",
        values=["cantidad", "total_venta"],
        aggfunc="sum",
    ).rename(columns={"cantidad": "unidades_vendidas", "total_venta": "ingreso_total"})

    producto_mas_vendido = resumen_producto["unidades_vendidas"].idxmax()
    producto_menos_vendido = resumen_producto["unidades_vendidas"].idxmin()
    producto_mayor_ingreso = resumen_producto["ingreso_total"].idxmax()
    producto_menor_ingreso = resumen_producto["ingreso_total"].idxmin()

    return {
        "producto_mas_vendido": producto_mas_vendido,
        "producto_menos_vendido": producto_menos_vendido,
        "producto_mayor_ingreso": producto_mayor_ingreso,
        "producto_menor_ingreso": producto_menor_ingreso,
        "resumen_producto": resumen_producto.reset_index(),
    }


# CONSULTAS ADICIONALES CON query() Y concat() (investigación obligatoria)
def ventas_altas_bogota(ventas, clientes, umbral=500_000):
    """
    Ejemplo de uso de query(): filtra ventas superiores a un umbral
    realizadas por clientes de Bogotá, combinando merge() + query().
    """
    ventas_con_cliente = ventas.merge(clientes, on="cliente_id", how="left")
    return ventas_con_cliente.query("ciudad == 'Bogotá' and total_venta > @umbral")


def consolidar_resumen_categorias(productos):
    """
    Ejemplo de uso de concat(): separa el catálogo de productos en dos
    bloques (por precio) y los vuelve a unir en un solo DataFrame,
    simulando la consolidación de reportes parciales de distintas fuentes.
    """
    baratos = productos[productos["precio_unitario"] < 200_000]
    costosos = productos[productos["precio_unitario"] >= 200_000]
    return pd.concat([baratos, costosos], axis=0).reset_index(drop=True)


# 6.6 GENERACIÓN DE REPORTE
def generar_reporte_excel(resumen, ventas, clientes, productos):
    """
    Genera reports/reporte_final.xlsx con las hojas Resumen, Ventas,
    Clientes y Productos, tal como lo exige el requerimiento 6.6.
    """
    os.makedirs("reports", exist_ok=True)

    resumen_df = pd.DataFrame(list(resumen.items()), columns=["Indicador", "Valor"])

    with pd.ExcelWriter(RUTA_REPORTE, engine="openpyxl") as writer:
        resumen_df.to_excel(writer, sheet_name="Resumen", index=False)
        ventas.to_excel(writer, sheet_name="Ventas", index=False)
        clientes.to_excel(writer, sheet_name="Clientes", index=False)
        productos.to_excel(writer, sheet_name="Productos", index=False)

    print(f"\nReporte generado en: {RUTA_REPORTE}")


def construir_resumen_general(indicadores_ventas, indicadores_clientes, indicadores_productos):
    """Combina todos los indicadores calculados en un solo diccionario plano."""
    return {
        "Total de ventas ($)": round(indicadores_ventas["total_ventas"], 0),
        "Promedio por venta ($)": round(indicadores_ventas["promedio_venta"], 0),
        "Venta máxima ($)": indicadores_ventas["venta_maxima"],
        "Venta mínima ($)": indicadores_ventas["venta_minima"],
        "Número de transacciones": indicadores_ventas["num_transacciones"],
        "Cliente con más compras": indicadores_clientes["cliente_mas_compras"][0],
        "Cliente que más ha gastado": indicadores_clientes["cliente_mayor_gasto"][0],
        "Ciudad con más clientes": indicadores_clientes["ciudad_mayor_clientes"][0],
        "Promedio de compra por cliente ($)": round(indicadores_clientes["promedio_compra_por_cliente"], 0),
        "Producto más vendido": indicadores_productos["producto_mas_vendido"],
        "Producto menos vendido": indicadores_productos["producto_menos_vendido"],
        "Producto con mayor ingreso": indicadores_productos["producto_mayor_ingreso"],
        "Producto con menor ingreso": indicadores_productos["producto_menor_ingreso"],
    }


def mostrar_resumen(resumen):
    """Muestra el resumen ejecutivo en consola de forma organizada."""
    print("\n" + "=" * 60)
    print("RESUMEN EJECUTIVO - TECNOANDINA S.A.S.")
    print("=" * 60)
    for indicador, valor in resumen.items():
        print(f"{indicador:.<45} {valor}")
    print("=" * 60)


def main():
    """Función principal que orquesta todo el flujo de análisis."""
    clientes, productos, ventas = cargar_datos()

    # La exploración (incluye conteo de nulos) se hace ANTES de limpiar,
    # para que el requerimiento 6.2 refleje el estado real de los datos.
    explorar_dataframe(clientes, "CLIENTES")
    explorar_dataframe(productos, "PRODUCTOS")
    explorar_dataframe(ventas, "VENTAS")

    clientes, productos, ventas = validar_datos(clientes, productos, ventas)

    indicadores_ventas = analizar_ventas(ventas)
    indicadores_clientes = analizar_clientes(clientes, ventas)
    indicadores_productos = analizar_productos(productos, ventas)

    # Ejemplos adicionales de funciones investigadas (query, concat)
    ventas_bogota_altas = ventas_altas_bogota(ventas, clientes)
    print(f"\nVentas > $500.000 en Bogotá (query()): {len(ventas_bogota_altas)} registros")

    catalogo_consolidado = consolidar_resumen_categorias(productos)
    print(f"Catálogo consolidado con concat(): {len(catalogo_consolidado)} productos")

    resumen = construir_resumen_general(indicadores_ventas, indicadores_clientes, indicadores_productos)
    mostrar_resumen(resumen)

    generar_reporte_excel(resumen, ventas, clientes, productos)


if __name__ == "__main__":
    main()