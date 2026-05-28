from pathlib import Path
import re
import sys
from typing import Dict, List

PROJECT_ROOT = Path(__file__).resolve().parents[1]
DEPS_DIR = PROJECT_ROOT / ".deps"
if DEPS_DIR.exists():
    sys.path.insert(0, str(DEPS_DIR))

from openpyxl import Workbook
from pypdf import PdfReader

INPUT_DIR = PROJECT_ROOT / "input"
OUTPUT_DIR = PROJECT_ROOT / "output"
OUTPUT_DIR.mkdir(exist_ok=True)

OUTPUT_XLSX = OUTPUT_DIR / "reporte_comprobantes.xlsx"
OUTPUT_PREVIEW = OUTPUT_DIR / "extraccion_preview.txt"


def extraer_texto_pdf(path: Path) -> str:
    reader = PdfReader(str(path))
    return "\n".join((page.extract_text() or "") for page in reader.pages)


def buscar(patron: str, texto: str, default: str = "") -> str:
    match = re.search(patron, texto, flags=re.IGNORECASE)
    return match.group(1).strip() if match else default


def normalizar_importe(valor: str) -> float:
    valor = (valor or "0").replace("$", "").replace(" ", "").strip()
    valor = valor.replace(".", "").replace(",", ".")
    return float(valor) if valor else 0.0


def validar_registro(registro: Dict) -> Dict:
    observaciones: List[str] = []

    obligatorios = ["Fecha", "Proveedor", "CUIT", "Nº comprobante"]
    faltantes = [campo for campo in obligatorios if not registro.get(campo)]
    if faltantes:
        observaciones.append(f"Faltan campos: {', '.join(faltantes)}")

    diferencia = abs((registro["Neto"] + registro["IVA"]) - registro["Total"])
    if diferencia > 1.0:
        observaciones.append("Neto + IVA no coincide con Total")

    if observaciones:
        registro["Estado extraccion"] = "Con alertas"
        registro["Observaciones"] = " | ".join(observaciones)
    else:
        registro["Estado extraccion"] = "OK"
        registro["Observaciones"] = ""
    return registro


def extraer_campos(path: Path) -> Dict:
    texto = extraer_texto_pdf(path)
    registro = {
        "Fecha": buscar(r"Fecha:\s*(\d{2}/\d{2}/\d{4})", texto),
        "Proveedor": buscar(r"Proveedor:\s*(.+)", texto),
        "CUIT": buscar(r"CUIT:\s*([0-9\-]+)", texto),
        "Nº comprobante": buscar(r"N[º°]\s*comprobante:\s*([0-9\-]+)", texto),
        "Neto": normalizar_importe(buscar(r"Neto gravado:\s*\$\s*([0-9\.,]+)", texto, "0")),
        "IVA": normalizar_importe(buscar(r"IVA 21%:\s*\$\s*([0-9\.,]+)", texto, "0")),
        "Total": normalizar_importe(buscar(r"Total:\s*\$\s*([0-9\.,]+)", texto, "0")),
        "Archivo origen": path.name,
        "Estado extraccion": "",
        "Observaciones": "",
    }
    return validar_registro(registro)


def exportar_excel(registros: List[Dict]) -> None:
    wb = Workbook()
    ws = wb.active
    ws.title = "Comprobantes"

    columnas = [
        "Fecha", "Proveedor", "CUIT", "Nº comprobante", "Neto", "IVA", "Total",
        "Estado extraccion", "Observaciones", "Archivo origen",
    ]
    ws.append(columnas)
    for reg in registros:
        ws.append([reg[c] for c in columnas])
    wb.save(OUTPUT_XLSX)


def exportar_preview(registros: List[Dict]) -> None:
    OUTPUT_PREVIEW.write_text("\n".join(str(reg) for reg in registros), encoding="utf-8")


def main() -> int:
    pdfs = sorted(INPUT_DIR.glob("*.pdf"))
    if not pdfs:
        print(f"No se encontraron PDFs en: {INPUT_DIR}")
        return 1

    registros: List[Dict] = []
    for path in pdfs:
        try:
            registros.append(extraer_campos(path))
        except Exception as exc:
            registros.append({
                "Fecha": "", "Proveedor": "", "CUIT": "", "Nº comprobante": "",
                "Neto": 0.0, "IVA": 0.0, "Total": 0.0,
                "Estado extraccion": "Error", "Observaciones": str(exc),
                "Archivo origen": path.name,
            })

    exportar_excel(registros)
    exportar_preview(registros)

    total = len(registros)
    ok = sum(1 for r in registros if r["Estado extraccion"] == "OK")
    alertas = sum(1 for r in registros if r["Estado extraccion"] in {"Con alertas", "Error"})

    print(f"Comprobantes procesados: {total}")
    print(f"Extraccion OK: {ok}")
    print(f"Con alertas/errores: {alertas}")
    print(f"Excel generado: {OUTPUT_XLSX}")
    print(f"Preview tecnico: {OUTPUT_PREVIEW}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
