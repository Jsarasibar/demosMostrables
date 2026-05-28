# Demo 2 - PDFs / comprobantes a Excel

Esta demo muestra cómo automatizar la carga de datos desde comprobantes PDF hacia una planilla ordenada.

## Problema

Un contador, administrativo o comercio recibe varios comprobantes en PDF y tiene que copiar a mano datos como fecha, proveedor, CUIT, número de comprobante, neto, IVA y total.

## Entrada

Los PDFs simulados están en:

```txt
input/
  factura_001.pdf
  factura_002.pdf
  factura_003.pdf
  factura_004.pdf
  factura_005.pdf
  factura_006.pdf
```

## Salida

El archivo generado está en:

```txt
output/reporte_comprobantes.xlsx
```

Columnas generadas:

```txt
Fecha | Proveedor | CUIT | Nº comprobante | Neto | IVA | Total | Archivo origen
```

## Qué demuestra

- Menos carga manual.
- Menos errores de tipeo.
- Datos ordenados en Excel.
- Trazabilidad: cada fila conserva el archivo PDF de origen.
- Utilidad para estudios contables, administrativos, comercios y profesionales.

## Mensaje comercial

Antes: varios comprobantes en PDF y carga manual en Excel.

Después: una planilla ordenada con los datos principales extraídos automáticamente.

Ideal para: estudios contables, administrativos, comercios y profesionales.

## Nota

Los comprobantes son simulados para una demo comercial. No son facturas reales.
