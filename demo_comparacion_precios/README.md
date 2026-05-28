# Demo - Comparacion de precios

## Objetivo
Mostrar como pasar de revisar precios manualmente pagina por pagina a una comparacion automatizada y trazable.

## Problema (Antes)
- El equipo revisa multiples sitios a mano.
- Se pierde tiempo consolidando resultados.
- Es facil cometer errores al copiar/preparar datos.

## Automatizacion
- Entrada: `input/productos_a_revisar.csv`
- Proceso: lectura de HTMLs simulados + extraccion de campos + validaciones por fila.
- Salida: `output/comparacion_precios_extraida.csv`

## Resultado (Despues)
- Precios comparables por producto.
- Identificacion automatica del proveedor mas barato.
- Trazabilidad por archivo origen y alertas de extraccion.

## Como ejecutar
```bash
python src/generar_comparacion_precios.py
```

## Archivos clave
- Script: `src/generar_comparacion_precios.py`
- Input: `input/productos_a_revisar.csv`
- Output: `output/comparacion_precios_extraida.csv`

## Checklist de demo
- Corre en menos de 30s.
- Genera salida aunque falle alguna fila.
- Muestra casos de disponible/sin stock/consultar.
- Permite responder rapido: "quien vende mas barato".
