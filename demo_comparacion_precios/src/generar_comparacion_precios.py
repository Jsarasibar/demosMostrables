"""
Demo: extraccion de datos publicos desde paginas simuladas.

Entrada:
  input/productos_a_revisar.csv
Salida:
  output/comparacion_precios_extraida.csv
"""

import csv
import re
from datetime import date
from pathlib import Path

INPUT_CSV = Path("input/productos_a_revisar.csv")
OUTPUT_CSV = Path("output/comparacion_precios_extraida.csv")


def limpiar_html(valor: str) -> str:
    return re.sub(r"<.*?>", "", valor, flags=re.S).strip()


def extraer_campo(html: str, clase: str) -> str:
    patron = rf'class="{clase}"[^>]*>(.*?)</'
    match = re.search(patron, html, flags=re.S)
    return limpiar_html(match.group(1)) if match else ""


def normalizar_estado(estado: str, precio_texto: str, precio_actual):
    estado_limpio = (estado or "").strip().lower()
    precio_limpio = (precio_texto or "").strip().lower()
    if "sin stock" in estado_limpio:
        return "Sin stock"
    if "dispon" in estado_limpio:
        return "Disponible"
    if "consultar" in estado_limpio or precio_limpio == "consultar":
        return "Consultar"
    if precio_actual == "":
        return "Consultar"
    return "Revisar"


def extraer_precio(precio_texto: str):
    match = re.search(r"[\d\.]+", precio_texto)
    if not match or precio_texto.lower().strip() == "consultar":
        return ""
    return int(match.group(0).replace(".", ""))


def extraer_producto(path_html: Path, producto_fallback: str, sitio_fallback: str) -> dict:
    html = path_html.read_text(encoding="utf-8")
    producto = extraer_campo(html, "product-name") or producto_fallback
    sitio = extraer_campo(html, "store-name") or sitio_fallback
    precio_texto = extraer_campo(html, "price")
    precio_actual = extraer_precio(precio_texto)
    estado = normalizar_estado(extraer_campo(html, "availability"), precio_texto, precio_actual)
    observaciones = extraer_campo(html, "notes")
    error_extraccion = ""

    if not producto or not sitio:
        estado = "Revisar"
        error_extraccion = "Faltan campos obligatorios (Producto/Sitio)"

    return {
        "Producto": producto,
        "Sitio": sitio,
        "Precio actual": precio_actual,
        "Precio minimo_por_producto": "",
        "Diferencia_vs_minimo": "",
        "Proveedor_mas_barato": "",
        "Fecha revision": date.today().isoformat(),
        "Estado": estado,
        "Observaciones": observaciones,
        "Error extraccion": error_extraccion,
        "Archivo origen": str(path_html),
    }


def agregar_metricas_comparacion(resultados):
    minimos_por_producto = {}
    proveedor_barato = {}

    for fila in resultados:
        producto = fila["Producto"]
        precio = fila["Precio actual"]
        if precio == "":
            continue
        minimo_actual = minimos_por_producto.get(producto)
        if minimo_actual is None or precio < minimo_actual:
            minimos_por_producto[producto] = precio
            proveedor_barato[producto] = fila["Sitio"]

    for fila in resultados:
        producto = fila["Producto"]
        precio = fila["Precio actual"]
        minimo = minimos_por_producto.get(producto, "")
        fila["Precio minimo_por_producto"] = minimo
        fila["Proveedor_mas_barato"] = proveedor_barato.get(producto, "")
        if precio == "" or minimo == "":
            fila["Diferencia_vs_minimo"] = ""
        else:
            fila["Diferencia_vs_minimo"] = precio - minimo


def main():
    OUTPUT_CSV.parent.mkdir(exist_ok=True)

    with INPUT_CSV.open("r", encoding="utf-8", newline="") as archivo:
        productos = list(csv.DictReader(archivo))

    resultados = []
    for fila in productos:
        url_relativa = (fila.get("URL") or "").strip()
        url_local = Path("input") / url_relativa
        try:
            if not url_relativa:
                raise ValueError("URL vacia en CSV")
            if not url_local.exists():
                raise FileNotFoundError(f"No existe el archivo: {url_local}")
            resultado = extraer_producto(
                url_local,
                producto_fallback=(fila.get("Producto") or "").strip(),
                sitio_fallback=(fila.get("Sitio") or "").strip(),
            )
        except Exception as exc:
            resultado = {
                "Producto": (fila.get("Producto") or "").strip(),
                "Sitio": (fila.get("Sitio") or "").strip(),
                "Precio actual": "",
                "Precio minimo_por_producto": "",
                "Diferencia_vs_minimo": "",
                "Proveedor_mas_barato": "",
                "Fecha revision": date.today().isoformat(),
                "Estado": "Revisar",
                "Observaciones": "",
                "Error extraccion": str(exc),
                "Archivo origen": str(url_local),
            }
        resultados.append(resultado)

    agregar_metricas_comparacion(resultados)

    columnas = [
        "Producto",
        "Sitio",
        "Precio actual",
        "Precio minimo_por_producto",
        "Diferencia_vs_minimo",
        "Proveedor_mas_barato",
        "Fecha revision",
        "Estado",
        "Observaciones",
        "Error extraccion",
        "Archivo origen",
    ]

    with OUTPUT_CSV.open("w", encoding="utf-8", newline="") as archivo:
        writer = csv.DictWriter(archivo, fieldnames=columnas)
        writer.writeheader()
        writer.writerows(resultados)

    filas_sin_precio = sum(1 for fila in resultados if fila["Precio actual"] == "")
    filas_baratas = sum(
        1
        for fila in resultados
        if fila["Precio actual"] != "" and fila["Diferencia_vs_minimo"] == 0
    )
    filas_con_error = sum(1 for fila in resultados if fila["Error extraccion"])

    print(f"Datos extraidos: {len(resultados)}")
    print(f"Sin precio: {filas_sin_precio}")
    print(f"Con mejor precio por producto: {filas_baratas}")
    print(f"Con error de extraccion: {filas_con_error}")
    print(f"Archivo generado: {OUTPUT_CSV}")


if __name__ == "__main__":
    main()
