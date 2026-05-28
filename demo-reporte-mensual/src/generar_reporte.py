from pathlib import Path
import sys

PROJECT_ROOT = Path(__file__).resolve().parents[1]
DEPS_DIR = PROJECT_ROOT / ".deps"
if DEPS_DIR.exists():
    sys.path.insert(0, str(DEPS_DIR))

import pandas as pd

INPUT_DIR = PROJECT_ROOT / "input"
OUTPUT_DIR = PROJECT_ROOT / "output"
OUTPUT_DIR.mkdir(exist_ok=True)

VENTAS_PATH = INPUT_DIR / "ventas_enero.csv"
GASTOS_PATH = INPUT_DIR / "gastos_enero.csv"
CLIENTES_PATH = INPUT_DIR / "clientes.xlsx"
REPORTE_PATH = OUTPUT_DIR / "reporte_mensual.xlsx"

MESES_ES = {
    1: "ENERO", 2: "FEBRERO", 3: "MARZO", 4: "ABRIL", 5: "MAYO", 6: "JUNIO",
    7: "JULIO", 8: "AGOSTO", 9: "SEPTIEMBRE", 10: "OCTUBRE", 11: "NOVIEMBRE", 12: "DICIEMBRE",
}


def normalizar_descuento(descuento_serie: pd.Series) -> pd.Series:
    """Normaliza descuento a formato tasa (0.05 = 5%)."""
    descuento = pd.to_numeric(descuento_serie, errors="coerce").fillna(0.0)
    # Si viene como 5, 10, 12 => convertir a 0.05, 0.10, 0.12
    return descuento.where(descuento <= 1, descuento / 100)


def cargar_datos():
    """Lee y tipa los archivos de entrada de la demo."""
    ventas = pd.read_csv(VENTAS_PATH)
    gastos = pd.read_csv(GASTOS_PATH)
    clientes = pd.read_excel(CLIENTES_PATH)

    ventas["fecha"] = pd.to_datetime(ventas["fecha"], errors="coerce")
    gastos["fecha"] = pd.to_datetime(gastos["fecha"], errors="coerce")
    clientes["fecha_alta"] = pd.to_datetime(clientes["fecha_alta"], errors="coerce")

    return ventas, gastos, clientes


def preparar_calidad_datos(ventas, gastos, clientes):
    """Completa faltantes basicos para que los agrupamientos sean robustos."""
    ventas = ventas.copy()
    gastos = gastos.copy()
    clientes = clientes.copy()

    ventas["categoria"] = ventas["categoria"].fillna("Sin categoria")
    ventas["canal"] = ventas["canal"].fillna("Sin canal")
    ventas["producto"] = ventas["producto"].fillna("Producto no informado")
    ventas["id_cliente"] = ventas["id_cliente"].fillna("SIN_CLIENTE")

    gastos["categoria_gasto"] = gastos["categoria_gasto"].fillna("Sin categoria")
    gastos["monto"] = pd.to_numeric(gastos["monto"], errors="coerce").fillna(0)

    clientes["nombre"] = clientes["nombre"].fillna("Cliente sin nombre")
    clientes["tipo_cliente"] = clientes["tipo_cliente"].fillna("Sin tipo")
    clientes["ciudad"] = clientes["ciudad"].fillna("Sin ciudad")

    return ventas, gastos, clientes


def determinar_periodo(ventas, gastos):
    """Deriva mes y anio del conjunto de fechas disponible."""
    fechas = pd.concat([ventas["fecha"], gastos["fecha"]], ignore_index=True).dropna()
    if fechas.empty:
        return "PERIODO SIN FECHAS"

    fecha_ref = fechas.min()
    mes = MESES_ES.get(int(fecha_ref.month), "MES")
    return f"{mes} {int(fecha_ref.year)}"


def procesar_datos(ventas, gastos, clientes):
    """Limpia, cruza y resume los datos principales."""
    ventas["descuento_norm"] = normalizar_descuento(ventas["descuento"])
    ventas["subtotal"] = ventas["cantidad"] * ventas["precio_unitario"]
    ventas["total_venta"] = ventas["subtotal"] * (1 - ventas["descuento_norm"])

    ventas_procesadas = ventas.merge(clientes, on="id_cliente", how="left")

    # Fallback final para clientes no encontrados en merge.
    ventas_procesadas["nombre"] = ventas_procesadas["nombre"].fillna("Cliente no encontrado")
    ventas_procesadas["tipo_cliente"] = ventas_procesadas["tipo_cliente"].fillna("Sin tipo")
    ventas_procesadas["ciudad"] = ventas_procesadas["ciudad"].fillna("Sin ciudad")

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
        "Clientes unicos": ventas_procesadas["id_cliente"].nunique(),
    }

    productos = (
        ventas_procesadas
        .groupby("producto", as_index=False)
        .agg(unidades_vendidas=("cantidad", "sum"), total_facturado=("total_venta", "sum"))
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
        .agg(compras=("id_venta", "count"), total_comprado=("total_venta", "sum"))
        .sort_values("total_comprado", ascending=False)
    )

    control_calidad = pd.DataFrame([
        {"control": "Ventas sin fecha valida", "cantidad": int(ventas_procesadas["fecha"].isna().sum())},
        {"control": "Gastos sin fecha valida", "cantidad": int(gastos["fecha"].isna().sum())},
        {"control": "Ventas sin cliente mapeado", "cantidad": int((ventas_procesadas["nombre"] == "Cliente no encontrado").sum())},
        {"control": "Ventas con total <= 0", "cantidad": int((ventas_procesadas["total_venta"] <= 0).sum())},
    ])

    return {
        "ventas_procesadas": ventas_procesadas,
        "gastos": gastos,
        "metricas": metricas,
        "productos": productos,
        "ventas_categoria": ventas_categoria,
        "gastos_categoria": gastos_categoria,
        "ventas_canal": ventas_canal,
        "clientes_resumen": clientes_resumen,
        "control_calidad": control_calidad,
    }


def escribir_reporte(data, periodo_texto):
    """Genera el Excel final con hojas, resumen y graficos."""
    with pd.ExcelWriter(REPORTE_PATH, engine="xlsxwriter") as writer:
        workbook = writer.book

        fmt_titulo = workbook.add_format({
            "bold": True, "font_size": 16, "font_color": "white", "bg_color": "#1F4E78",
            "align": "center", "valign": "vcenter",
        })
        fmt_header = workbook.add_format({
            "bold": True, "font_color": "white", "bg_color": "#305496", "border": 1, "align": "center",
        })
        fmt_moneda = workbook.add_format({"num_format": "$ #,##0"})
        fmt_numero = workbook.add_format({"num_format": "#,##0"})
        fmt_texto = workbook.add_format({"text_wrap": True, "valign": "top"})

        resumen = workbook.add_worksheet("Resumen")
        writer.sheets["Resumen"] = resumen

        resumen.merge_range("A1:H1", f"REPORTE MENSUAL AUTOMATICO - LIBRERIA | {periodo_texto}", fmt_titulo)

        metricas = data["metricas"]
        resumen.write_row("A3", ["Metrica", "Valor"], fmt_header)

        filas_metricas = [
            ["Total vendido", metricas["Total vendido"]],
            ["Total gastado", metricas["Total gastado"]],
            ["Ganancia estimada", metricas["Ganancia estimada"]],
            ["Cantidad de ventas", metricas["Cantidad de ventas"]],
            ["Unidades vendidas", metricas["Unidades vendidas"]],
            ["Ticket promedio", metricas["Ticket promedio"]],
            ["Clientes unicos", metricas["Clientes unicos"]],
        ]

        for i, fila in enumerate(filas_metricas, start=3):
            resumen.write(i, 0, fila[0])
            resumen.write(i, 1, fila[1], fmt_moneda if i in [3, 4, 5, 8] else fmt_numero)

        producto_top = data["productos"].iloc[0]["producto"] if not data["productos"].empty else "N/D"
        categoria_top = data["ventas_categoria"].iloc[0]["categoria"] if not data["ventas_categoria"].empty else "N/D"
        canal_top = data["ventas_canal"].iloc[0]["canal"] if not data["ventas_canal"].empty else "N/D"

        resumen.write_row("D3", ["Indicador", "Resultado"], fmt_header)
        resumen.write_row("D4", ["Producto mas vendido", producto_top])
        resumen.write_row("D5", ["Categoria con mas facturacion", categoria_top])
        resumen.write_row("D6", ["Canal con mas ventas", canal_top])

        texto_resumen = (
            f"Durante {periodo_texto} se registraron {metricas['Cantidad de ventas']:.0f} ventas "
            f"y {metricas['Unidades vendidas']:.0f} unidades vendidas. "
            f"El total vendido fue de ${metricas['Total vendido']:,.0f}, "
            f"mientras que los gastos sumaron ${metricas['Total gastado']:,.0f}. "
            f"La ganancia estimada fue de ${metricas['Ganancia estimada']:,.0f}."
        )

        resumen.write("A12", "Resumen mensual", fmt_header)
        resumen.merge_range("A13:H15", texto_resumen, fmt_texto)

        data["productos"].to_excel(writer, sheet_name="Productos destacados", index=False)
        data["ventas_categoria"].to_excel(writer, sheet_name="Ventas por categoria", index=False)
        data["gastos_categoria"].to_excel(writer, sheet_name="Gastos", index=False)
        data["clientes_resumen"].to_excel(writer, sheet_name="Clientes", index=False)
        data["ventas_procesadas"].to_excel(writer, sheet_name="Datos procesados", index=False)
        data["gastos"].to_excel(writer, sheet_name="Datos gastos", index=False)
        data["control_calidad"].to_excel(writer, sheet_name="Control calidad", index=False)

        for sheet_name in writer.sheets:
            ws = writer.sheets[sheet_name]
            ws.set_column("A:A", 24)
            ws.set_column("B:B", 24)
            ws.set_column("C:H", 18)

        data["ventas_categoria"].to_excel(writer, sheet_name="Resumen", startrow=17, startcol=0, index=False)
        data["productos"].head(5)[["producto", "unidades_vendidas"]].to_excel(
            writer, sheet_name="Resumen", startrow=17, startcol=3, index=False
        )

        chart_cat = workbook.add_chart({"type": "column"})
        chart_cat.add_series({
            "name": "Ventas por categoria",
            "categories": ["Resumen", 18, 0, 18 + len(data["ventas_categoria"]) - 1, 0],
            "values": ["Resumen", 18, 1, 18 + len(data["ventas_categoria"]) - 1, 1],
        })
        chart_cat.set_title({"name": "Ventas por categoria"})
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
    ventas, gastos, clientes = preparar_calidad_datos(ventas, gastos, clientes)
    periodo_texto = determinar_periodo(ventas, gastos)
    data = procesar_datos(ventas, gastos, clientes)
    escribir_reporte(data, periodo_texto)


if __name__ == "__main__":
    main()
