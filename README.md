# Sistema de Análisis Empresarial con Pandas — Actividad de Aprendizaje No. 4

**Empresa simulada:** TecnoAndina S.A.S.
**Programa:** ADSO - SENA CTMA
**Instructor:** Efren Moreno Valoyes

## Descripción

Aplicación en Python y Pandas que carga, explora, analiza y genera reportes
automáticos a partir de información empresarial (clientes, productos y
ventas) almacenada en archivos CSV y Excel.

## Requisitos

```bash
pip install -r requirements.txt
```

## Estructura del repositorio

```
proyecto-pandas/
├── data/
│   ├── clientes.csv       (34 registros)
│   ├── productos.xlsx     (22 registros)
│   └── ventas.csv         (220 registros)
├── src/
│   └── analisis.py
├── reports/
│   └── reporte_final.xlsx (generado al ejecutar el programa)
├── manual_tecnico_pandas.pdf
├── README.md
└── requirements.txt
```

## Cómo ejecutar

Desde la raíz del repositorio:

```bash
python3 src/analisis.py
```

El programa imprime en consola la exploración de datos y el resumen
ejecutivo, y genera `reports/reporte_final.xlsx` con las hojas **Resumen**,
**Ventas**, **Clientes** y **Productos**.

## Funciones de Pandas investigadas

`value_counts()`, `nunique()`, `drop_duplicates()`, `rename()`, `astype()`,
`query()`, `merge()`, `concat()`, `pivot_table()`, `groupby()`.
El detalle de cada una (qué hace, sintaxis, problema que resuelve y cómo se
usó) está documentado en `manual_tecnico_pandas.pdf`.

## Ventajas de automatizar con Python y Pandas

1. Velocidad y escalabilidad frente al análisis manual en Excel.
2. Reducción de errores humanos (fórmulas mal copiadas, referencias rotas).
3. Reproducibilidad: el mismo script genera siempre el mismo reporte.

**Riesgo:** si los datos de entrada contienen errores, el sistema los
propaga automáticamente a todos los indicadores sin que se note a simple
vista, por lo que la etapa de validación de datos es indispensable.

## Buenas prácticas aplicadas

- Funciones separadas por responsabilidad (carga, validación, exploración,
  análisis, reporte).
- Validación y limpieza de datos antes de calcular indicadores.
- Nombres descriptivos de variables y funciones.
- Código comentado explicando el propósito de cada función usada.