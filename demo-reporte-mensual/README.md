# Demo - Reporte mensual automatico

## Objetivo
Mostrar como consolidar ventas, gastos y clientes en un reporte mensual unico listo para decision.

## Problema (Antes)
- Datos repartidos en archivos separados.
- Armado manual del reporte mensual.
- Poca visibilidad de metricas clave en un solo lugar.

## Automatizacion
- Entradas:
  - `input/ventas_enero.csv`
  - `input/gastos_enero.csv`
  - `input/clientes.xlsx`
- Proceso: limpieza, cruces, metricas, validaciones y visualizacion.
- Salida: `output/reporte_mensual.xlsx`

## Resultado (Despues)
- Resumen ejecutivo con KPI.
- Tablas por producto/categoria/canal/clientes.
- Hoja de control de calidad para dar confianza en los datos.

## Como ejecutar
```bash
python -m pip install -r requirements.txt --target .deps
python src/generar_reporte.py
```

## Archivos clave
- Script: `src/generar_reporte.py`
- Output principal: `output/reporte_mensual.xlsx`

## Checklist de demo
- Titulo del reporte sale del periodo real de datos.
- Regla de descuento correctamente normalizada.
- El reporte se genera sin errores.
- Incluye hoja de control de calidad.
