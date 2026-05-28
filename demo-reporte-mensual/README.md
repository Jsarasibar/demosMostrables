# Demo: reporte mensual automático para librería

Esta demo muestra cómo transformar archivos separados de ventas, gastos y clientes en un único reporte mensual en Excel.

## Entrada

Los archivos de entrada están en la carpeta `input/`:

- `ventas_enero.csv`
- `gastos_enero.csv`
- `clientes.xlsx`

## Salida

El reporte final se genera en:

- `output/reporte_mensual.xlsx`

## Cómo ejecutar

```bash
pip install -r requirements.txt
python src/generar_reporte.py
```

## Qué genera

El Excel final incluye:

- Resumen mensual
- Total vendido
- Total gastado
- Ganancia estimada
- Productos más vendidos
- Ventas por categoría
- Gastos por categoría
- Clientes
- Datos procesados
- Gráficos simples

## Nota comercial

La demo busca mostrar el antes/después:

Antes: datos separados en planillas.
Después: reporte automático listo para revisar.
