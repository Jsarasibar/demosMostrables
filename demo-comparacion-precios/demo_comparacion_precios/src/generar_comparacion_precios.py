"""
Demo: extracción de datos públicos desde páginas simuladas a Excel.

Entrada:
  input/productos_a_revisar.csv

Cada fila contiene:
  Producto | URL | Sitio

En esta demo las URLs apuntan a archivos HTML locales dentro de input/mock_web/.
En un caso real, el extractor se adaptaría a las páginas públicas del cliente.
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


def extraer_precio(precio_texto: str):
    match = re.search(r"[\d\.]+", precio_texto)
    if not match or precio_texto.lower().strip() == "consultar":
        return ""
    return int(match.group(0).replace(".", ""))


def extraer_producto(path_html: Path) -> dict:
    html = path_html.read_text(encoding="utf-8")
    return {
        "Producto": extraer_campo(html, "product-name"),
        "Sitio": extraer_campo(html, "store-name"),
        "Precio actual": extraer_precio(extraer_campo(html, "price")),
        "Fecha revisión": date.today().isoformat(),
        "Estado": extraer_campo(html, "availability"),
        "Observaciones": extraer_campo(html, "notes"),
        "Archivo origen": str(path_html),
    }


def main():
    OUTPUT_CSV.parent.mkdir(exist_ok=True)

    with INPUT_CSV.open("r", encoding="utf-8", newline="") as archivo:
        productos = list(csv.DictReader(archivo))

    resultados = []
    for fila in productos:
        url_local = Path("input") / fila["URL"]
        resultados.append(extraer_producto(url_local))

    columnas = [
        "Producto",
        "Sitio",
        "Precio actual",
        "Fecha revisión",
        "Estado",
        "Observaciones",
        "Archivo origen",
    ]

    with OUTPUT_CSV.open("w", encoding="utf-8", newline="") as archivo:
        writer = csv.DictWriter(archivo, fieldnames=columnas)
        writer.writeheader()
        writer.writerows(resultados)

    print(f"Datos extraídos: {len(resultados)}")
    print(f"Archivo generado: {OUTPUT_CSV}")


if __name__ == "__main__":
    main()
