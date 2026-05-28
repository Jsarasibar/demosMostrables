from pathlib import Path

import pandas as pd


INPUT_DIR = Path(__file__).resolve().parents[1] / "input"
OUTPUT_DIR = Path(__file__).resolve().parents[1] / "output"
OUTPUT_DIR.mkdir(exist_ok=True)

VENTAS_PATH = INPUT_DIR / "ventas_enero.csv"
GASTOS_PATH = INPUT_DIR / "gastos_enero.csv"
CLIENTES_PATH = INPUT_DIR / "clientes.xlsx"
REPORTE_PATH = OUTPUT_DIR / "reporte_mensual.xlsx"


def cargar_datos():
    """Lee los archivos de entrada de la demo."""
    ventas = pd.read_csv(VENTAS_PATH)
    gastos = pd.read_csv(GASTOS_PATH)
    clientes = pd.read_excel(CLIENTES_PATH)

    ventas["fecha"] = pd.to_datetime(ventas["fecha"])
    gastos["fecha"] = pd.to_datetime(gastos["fecha"])
    clientes["fecha_alta"] = pd.to_datetime(clientes["fecha_alta"])

    return ventas, gastos, clientes


def procesar_datos(ventas, gastos, clientes):
    """Limpia, cruza y resume los datos principales."""
    ventas["subtotal"] = ventas["cantidad"] * ventas["precio_unitario"]
    ventas["total_venta"] = ventas["subtotal"] * (1 - ventas["descuento"] / 100)

    ventas_procesadas = ventas.merge(clientes, on="id_cliente", how="left")

    total_vendido = ventas_procesadas["total_venta"].sum()
    total_gastado = gastos["monto"].sum()
    cantidad_ventas = len(ventas_procesadas)

    metricas = {
        "Total vendido": total_vendido,
        "Total gastado": total_gastado,
        "Ganancia estimada": total_vendido - total_gastado,
        "Cantidad de ventas": cantidad_ventas,
        "Unidades vendidas": ventas_procesadas["cantidad"].sum(),
        "Ticket promedio": total_vendido / cantidad_ventas if cantidad_ventas else 0,
        "Clientes únicos": ventas_procesadas["id_cliente"].nunique(),
    }

    productos = (
        ventas_procesadas
        .groupby("producto", as_index=False)
        .agg(
            unidades_vendidas=("cantidad", "sum"),
            total_facturado=("total_venta", "sum"),
        )
        .sort_values(["unidades_vendidas", "total_facturado"], ascending=False)
    )

    ventas_categoria = (
        ventas_procesadas
        .groupby("categoria", as_index=False)
        .agg(total_vendido=("total_venta", "sum"))
        .sort_values("total_vendido", ascending=False)
    )

    gastos_categoria = (
        gastos
        .groupby("categoria_gasto", as_index=False)
        .agg(total_gastado=("monto", "sum"))
        .sort_values("total_gastado", ascending=False)
    )

    ventas_canal = (
        ventas_procesadas
        .groupby("canal", as_index=False)
        .agg(total_vendido=("total_venta", "sum"))
        .sort_values("total_vendido", ascending=False)
    )

    clientes_resumen = (
        ventas_procesadas
        .groupby(["id_cliente", "nombre", "tipo_cliente", "ciudad"], as_index=False)
        .agg(
            compras=("id_venta", "count"),
            total_comprado=("total_venta", "sum"),
        )
        .sort_values("total_comprado", ascending=False)
    )

    return {
        "ventas_procesadas": ventas_procesadas,
        "gastos": gastos,
        "metricas": metricas,
        "productos": productos,
        "ventas_categoria": ventas_categoria,
        "gastos_categoria": gastos_categoria,
        "ventas_canal": ventas_canal,
        "clientes_resumen": clientes_resumen,
    }


def escribir_reporte(data):
    """Genera el Excel final con hojas, resumen y gráficos."""
    with pd.ExcelWriter(REPORTE_PATH, engine="xlsxwriter") as writer:
        workbook = writer.book

        # Formatos visuales.
        fmt_titulo = workbook.add_format({
            "bold": True,
            "font_size": 16,
            "font_color": "white",
            "bg_color": "#1F4E78",
            "align": "center",
            "valign": "vcenter",
        })
        fmt_header = workbook.add_format({
            "bold": True,
            "font_color": "white",
            "bg_color": "#305496",
            "border": 1,
            "align": "center",
        })
        fmt_moneda = workbook.add_format({"num_format": "$ #,##0"})
        fmt_numero = workbook.add_format({"num_format": "#,##0"})
        fmt_texto = workbook.add_format({"text_wrap": True, "valign": "top"})

        # Hoja resumen.
        resumen = workbook.add_worksheet("Resumen")
        writer.sheets["Resumen"] = resumen

        resumen.merge_range("A1:H1", "REPORTE MENSUAL AUTOMÁTICO - LIBRERÍA | ENERO 2026", fmt_titulo)

        metricas = data["metricas"]
        resumen.write_row("A3", ["Métrica", "Valor"], fmt_header)

        filas_metricas = [
            ["Total vendido", metricas["Total vendido"]],
            ["Total gastado", metricas["Total gastado"]],
            ["Ganancia estimada", metricas["Ganancia estimada"]],
            ["Cantidad de ventas", metricas["Cantidad de ventas"]],
            ["Unidades vendidas", metricas["Unidades vendidas"]],
            ["Ticket promedio", metricas["Ticket promedio"]],
            ["Clientes únicos", metricas["Clientes únicos"]],
        ]

        for i, fila in enumerate(filas_metricas, start=3):
            resumen.write(i, 0, fila[0])
            resumen.write(i, 1, fila[1], fmt_moneda if i in [3, 4, 5, 8] else fmt_numero)

        producto_top = data["productos"].iloc[0]["producto"]
        categoria_top = data["ventas_categoria"].iloc[0]["categoria"]
        canal_top = data["ventas_canal"].iloc[0]["canal"]

        resumen.write_row("D3", ["Indicador", "Resultado"], fmt_header)
        resumen.write_row("D4", ["Producto más vendido", producto_top])
        resumen.write_row("D5", ["Categoría con más facturación", categoria_top])
        resumen.write_row("D6", ["Canal con más ventas", canal_top])

        texto_resumen = (
            f"Durante enero se registraron {metricas['Cantidad de ventas']:.0f} ventas "
            f"y {metricas['Unidades vendidas']:.0f} unidades vendidas. "
            f"El total vendido fue de ${metricas['Total vendido']:,.0f}, "
            f"mientras que los gastos sumaron ${metricas['Total gastado']:,.0f}. "
            f"La ganancia estimada fue de ${metricas['Ganancia estimada']:,.0f}."
        )

        resumen.write("A12", "Resumen mensual", fmt_header)
        resumen.merge_range("A13:H15", texto_resumen, fmt_texto)

        # Hojas de detalle.
        data["productos"].to_excel(writer, sheet_name="Productos destacados", index=False)
        data["ventas_categoria"].to_excel(writer, sheet_name="Ventas por categoria", index=False)
        data["gastos_categoria"].to_excel(writer, sheet_name="Gastos", index=False)
        data["clientes_resumen"].to_excel(writer, sheet_name="Clientes", index=False)
        data["ventas_procesadas"].to_excel(writer, sheet_name="Datos procesados", index=False)
        data["gastos"].to_excel(writer, sheet_name="Datos gastos", index=False)

        for sheet_name in writer.sheets:
            ws = writer.sheets[sheet_name]
            ws.set_column("A:A", 22)
            ws.set_column("B:B", 22)
            ws.set_column("C:H", 18)

        # Datos auxiliares para gráficos dentro de Resumen.
        data["ventas_categoria"].to_excel(writer, sheet_name="Resumen", startrow=17, startcol=0, index=False)
        data["productos"].head(5)[["producto", "unidades_vendidas"]].to_excel(
            writer, sheet_name="Resumen", startrow=17, startcol=3, index=False
        )

        chart_cat = workbook.add_chart({"type": "column"})
        chart_cat.add_series({
            "name": "Ventas por categoría",
            "categories": ["Resumen", 18, 0, 18 + len(data["ventas_categoria"]) - 1, 0],
            "values": ["Resumen", 18, 1, 18 + len(data["ventas_categoria"]) - 1, 1],
        })
        chart_cat.set_title({"name": "Ventas por categoría"})
        chart_cat.set_legend({"none": True})
        resumen.insert_chart("A26", chart_cat)

        chart_prod = workbook.add_chart({"type": "bar"})
        chart_prod.add_series({
            "name": "Unidades vendidas",
            "categories": ["Resumen", 18, 3, 22, 3],
            "values": ["Resumen", 18, 4, 22, 4],
        })
        chart_prod.set_title({"name": "Top 5 productos"})
        chart_prod.set_legend({"none": True})
        resumen.insert_chart("E26", chart_prod)

    print(f"Reporte creado: {REPORTE_PATH}")


def main():
    ventas, gastos, clientes = cargar_datos()
    data = procesar_datos(ventas, gastos, clientes)
    escribir_reporte(data)


if __name__ == "__main__":
    main()
