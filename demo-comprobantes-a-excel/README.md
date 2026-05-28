# Demo - Comprobantes a Excel

## Objetivo
Mostrar como transformar PDFs de comprobantes en una planilla estructurada para revision administrativa/contable.

## Problema (Antes)
- Carga manual repetitiva desde PDF a Excel.
- Alto riesgo de errores de tipeo.
- Sin trazabilidad clara de origen por fila.

## Automatizacion
- Entrada: PDFs en `input/`
- Proceso: extraccion de texto + regex de campos + validaciones contables basicas.
- Salidas:
  - `output/reporte_comprobantes.xlsx`
  - `output/extraccion_preview.txt`

## Resultado (Despues)
- Datos estandarizados para analisis.
- Estado de extraccion por comprobante (OK/Con alertas/Error).
- Observaciones para revisar excepciones en vez de cargar todo manual.

## Como ejecutar
```bash
python -m pip install -r requirements.txt --target .deps
python src/generar_reporte_comprobantes.py
```

## Archivos clave
- Script: `src/generar_reporte_comprobantes.py`
- Input: `input/*.pdf`
- Output principal: `output/reporte_comprobantes.xlsx`
- Reporte de analisis/mejoras: `reporte_analisis_demo.txt`

## Checklist de demo
- Procesa todos los PDFs de input.
- Genera Excel y preview tecnico.
- Marca alertas cuando faltan campos o hay inconsistencias.
- Mantiene trazabilidad por archivo origen.
