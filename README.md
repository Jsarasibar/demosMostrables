# Demos mostrables - Guia rapida

Este repositorio incluye 3 demos simples para mostrar:
- problema
- automatizacion
- resultado final

## Demos
1. `demo_comparacion_precios`
2. `demo-comprobantes-a-excel`
3. `demo-reporte-mensual`

## Ejecucion
### 1) Comparacion de precios
```bash
cd demo_comparacion_precios
python src/generar_comparacion_precios.py
```

### 2) Comprobantes a Excel
```bash
cd demo-comprobantes-a-excel
python -m pip install -r requirements.txt --target .deps
python src/generar_reporte_comprobantes.py
```

### 3) Reporte mensual
```bash
cd demo-reporte-mensual
python -m pip install -r requirements.txt --target .deps
python src/generar_reporte.py
```

## Resultado esperado
- Cada demo genera un output claro y demostrable en su carpeta `output/`.
- Cada demo incluye `reporte_analisis_demo.txt` con hallazgos, mejoras y estado de correcciones.
