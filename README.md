## Gestión de Cuentas Corrientes (SQLite + CSV)

Proyecto con varios scripts Python que modelan cuentas corrientes, persisten datos en SQLite y exportan resultados a CSV. Cada archivo muestra una variante de la misma idea con pequeñas diferencias en el esquema y en la forma de ejecutar consultas.

### Requisitos

- Python 3.9+ (probado con Python 3 en macOS)
- Módulos estándar: `sqlite3`, `csv` (no hay dependencias externas)

### Archivos principales

- `Eva2.py`
	- Tablas: `CtaCte` y `Movimientos` (incluye `fecha` y `descripcion`).
	- Usa consultas parametrizadas (seguro contra inyección SQL).
	- Incluye ejemplo de uso y exporta cuentas a `CuentasCorrientes.csv`.

- `Eva2 Final.py` (recomendado para ejecutar)
	- Tablas: `ctacte` y `movimientos` (nombres en minúscula, con restricciones básicas).
	- Usa consultas parametrizadas y exporta cuentas y movimientos (`CuentasCorrientes.csv`, `Movimientos.csv`).
	- Mapea `tipoMovimiento`: 1 = depósito/abono, 0 = retiro/cargo.

- `prueba 6.py`
	- Tablas: `CtaCte` y `Movimientos`.
	- Construye SQL por interpolación de strings (no recomendado).
	- Exporta `CuentasCorrientes.csv` y `Movimientos.csv` agregando una columna `Descripcion` derivada ("abono"/"carga").

- `Prueba 5.py`
	- Similar a `prueba 6.py` pero la tabla `Movimientos` incluye columna `descripcion` y se guarda tal cual.
	- También usa interpolación de strings (no recomendado).

- `prueba final 4.py`
	- Variante con `ctacte`/`movimientos` y consultas parametrizadas.
	- Exporta `CuentasCorrientes.csv` y `MovimientosCuentas.csv`.

- Archivos generados
	- Base de datos: `MovimientosYCtaCte.db` o `MovimentosYCtaCte.db` (ver nota importante).
	- CSV: `CuentasCorrientes.csv`, `Movimientos.csv` (o `MovimientosCuentas.csv` en una variante).

### Cómo ejecutar (macOS/Linux)

Al ejecutar cualquiera de los scripts se crearán (si no existen) las tablas y algunos datos de ejemplo; luego se exportarán CSV.

```sh
# Ejecutar la variante recomendada
python3 "Eva2 Final.py"

# Otras variantes
python3 "Eva2.py"
python3 "prueba final 4.py"
python3 "Prueba 5.py"
python3 "prueba 6.py"
```

Sugerencia: debido a que varios archivos comparten nombres de tablas o la misma base de datos, ejecuta una sola variante por sesión si quieres resultados consistentes.

### Esquema y diferencias clave

- Nombres de tablas: algunas variantes usan `CtaCte`/`Movimientos` y otras `ctacte`/`movimientos`.
- Columnas extra: `Eva2.py` guarda `fecha` y `descripcion` en `Movimientos`; otras no.
- Tipo de movimiento: en general 1 = abono/deposito, 0 = cargo/retiro. Revisa el script si necesitas consistencia absoluta.
- Exportaciones: los nombres de los CSV varían levemente según el archivo.

### Notas importantes

- Inyección SQL: `Prueba 5.py` y `prueba 6.py` interpolan valores en strings SQL; prefiere `Eva2.py`, `Eva2 Final.py` o `prueba final 4.py` que usan parámetros (`?`).
- Nombre de la base de datos: hay dos variantes en el repositorio: `MovimientosYCtaCte.db` (correcto) y `MovimentosYCtaCte.db` (sin la segunda "i"). Esto puede crear dos archivos distintos. Si quieres unificar resultados, borra el archivo que no usarás y estandariza el nombre en el script que ejecutes.
- Reiniciar datos: basta con borrar el archivo `.db` antes de ejecutar de nuevo para recrear las tablas desde cero.

```sh
# Borrar la base para empezar de cero
rm -f MovimientosYCtaCte.db MovimentosYCtaCte.db
```

### Salidas esperadas

- `CuentasCorrientes.csv`: exporta todas las cuentas.
- `Movimientos.csv` o `MovimientosCuentas.csv`: exporta los movimientos (según la variante ejecutada).

### Próximos pasos sugeridos

- Unificar el nombre del archivo de base de datos y el esquema (mismas tablas/columnas en todas las variantes).
- Extraer la clase `CuentaCorriente` a un módulo reutilizable y crear un pequeño CLI (por ejemplo, `main.py`).
- Añadir timestamps en todas las variantes de `movimientos` y normalizar el significado de `tipoMovimiento`.
- Agregar tests mínimos para validar depósitos, retiros, y exportaciones.

