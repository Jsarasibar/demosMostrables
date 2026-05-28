from pathlib import Path
import re
import fitz  # PyMuPDF

INPUT_DIR = Path(__file__).resolve().parents[1] / 'input'
OUTPUT_DIR = Path(__file__).resolve().parents[1] / 'output'
OUTPUT_DIR.mkdir(exist_ok=True)

# Este script extrae campos de PDFs simulados de la demo.
# En un caso real se adaptarían los patrones al formato de comprobante del cliente.

def extraer_texto_pdf(path: Path) -> str:
    with fitz.open(path) as doc:
        return '\n'.join(page.get_text() for page in doc)


def buscar(patron: str, texto: str, default: str = '') -> str:
    match = re.search(patron, texto, flags=re.IGNORECASE)
    return match.group(1).strip() if match else default


def normalizar_importe(valor: str) -> float:
    valor = valor.replace('$', '').replace(' ', '').strip()
    valor = valor.replace('.', '').replace(',', '.')
    return float(valor)


def extraer_campos(path: Path) -> dict:
    texto = extraer_texto_pdf(path)
    fecha = buscar(r'Fecha:\s*(\d{2}/\d{2}/\d{4})', texto)
    proveedor = buscar(r'Proveedor:\s*(.+)', texto)
    cuit = buscar(r'CUIT:\s*([0-9\-]+)', texto)
    comprobante = buscar(r'N[º°]\s*comprobante:\s*([0-9\-]+)', texto)
    neto = buscar(r'Neto gravado:\s*\$\s*([0-9\.,]+)', texto, '0')
    iva = buscar(r'IVA 21%:\s*\$\s*([0-9\.,]+)', texto, '0')
    total = buscar(r'Total:\s*\$\s*([0-9\.,]+)', texto, '0')
    return {
        'Fecha': fecha,
        'Proveedor': proveedor,
        'CUIT': cuit,
        'Nº comprobante': comprobante,
        'Neto': normalizar_importe(neto),
        'IVA': normalizar_importe(iva),
        'Total': normalizar_importe(total),
        'Archivo origen': path.name,
    }


def main():
    registros = [extraer_campos(path) for path in sorted(INPUT_DIR.glob('*.pdf'))]
    # Para mantener el script liviano y fácil de revisar, imprime los registros extraídos.
    # En la demo final, estos registros se vuelcan a reporte_comprobantes.xlsx.
    for r in registros:
        print(r)


if __name__ == '__main__':
    main()
