# Guia de despliegue: dbt + BigQuery + Looker Studio

Esta guia permite desplegar el proyecto `dbt_202610` desde Visual Studio Code, ejecutar el pipeline en BigQuery y visualizar los resultados en Looker Studio.

## 1. Prerrequisitos

La persona que despliegue el proyecto necesita:

- Visual Studio Code.
- Python 3.12 recomendado.
- Git.
- Acceso al proyecto de Google Cloud:

```text
dbt-exam-project-490202
```

- Un archivo de service account JSON con permisos sobre BigQuery.
- Acceso a Looker Studio con una cuenta que pueda leer las tablas de BigQuery.

## 2. Clonar el repositorio

Abrir una terminal de PowerShell y ejecutar:

```powershell
cd $env:USERPROFILE\Downloads
mkdir dbt_202610_codex
cd dbt_202610_codex
git clone https://github.com/gfrieri/dbt_202610.git
cd dbt_202610
```

## 3. Abrir el proyecto en Visual Studio Code

Desde la misma terminal:

```powershell
code .
```

Si el comando `code .` no funciona, abrir VS Code manualmente y seleccionar:

```text
File > Open Folder > C:\Users\<USUARIO>\Downloads\dbt_202610_codex\dbt_202610
```

La carpeta que se abre en VS Code debe ser `dbt_202610`, no la carpeta contenedora `dbt_202610_codex`.

## 4. Crear y activar ambiente virtual

En la terminal integrada de VS Code:

```powershell
python -m venv venv
```

Activar el ambiente:

```powershell
.\venv\Scripts\Activate.ps1
```

Si PowerShell bloquea la activacion:

```powershell
Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass
.\venv\Scripts\Activate.ps1
```

Instalar dependencias:

```powershell
python -m pip install --upgrade pip
pip install -r requirements.txt
```

Validar dbt:

```powershell
dbt --version
```

Versiones usadas en la ejecucion validada:

```text
dbt-core 1.11.11
dbt-bigquery 1.11.1
```

## 5. Configurar profiles.yml

Crear una carpeta de profiles al lado del proyecto:

```powershell
cd ..
mkdir profiles
cd dbt_202610
```

Crear este archivo:

```text
C:\Users\<USUARIO>\Downloads\dbt_202610_codex\profiles\profiles.yml
```

Contenido del archivo:

```yaml
dbt_202610:
  target: dev
  outputs:
    dev:
      type: bigquery
      method: service-account
      project: dbt-exam-project-490202
      dataset: dbt_dataset
      keyfile: C:\RUTA\AL\service-account.json
      threads: 4
      timeout_seconds: 300
      location: US
      priority: interactive
```

Cambiar esta linea por la ruta real del archivo JSON:

```yaml
keyfile: C:\RUTA\AL\service-account.json
```

Ejemplo usado en esta maquina:

```yaml
keyfile: C:\Users\User\Downloads\Parcial1_DBT\Parcial1_DBT\keys\service-account.json
```

## 6. Validar conexion con BigQuery

Desde la carpeta del proyecto:

```powershell
cd C:\Users\<USUARIO>\Downloads\dbt_202610_codex\dbt_202610
.\venv\Scripts\Activate.ps1
dbt debug --profiles-dir "C:\Users\<USUARIO>\Downloads\dbt_202610_codex\profiles"
```

El resultado esperado debe terminar con:

```text
All checks passed!
```

## 7. Cargar datos raw en BigQuery

El proyecto usa dos fuentes raw:

```text
raw.raw_customers
raw.raw_orders
```

Se cargan desde estos archivos del repositorio:

```text
raw_data/raw_customers_updated.csv
raw_data/raw_orders_updated.csv
```

Ejecutar:

```powershell
.\venv\Scripts\python.exe .\scripts\load_raw_to_bigquery.py --project dbt-exam-project-490202 --keyfile "C:\RUTA\AL\service-account.json"
```

Ejemplo:

```powershell
.\venv\Scripts\python.exe .\scripts\load_raw_to_bigquery.py --project dbt-exam-project-490202 --keyfile "C:\Users\User\Downloads\Parcial1_DBT\Parcial1_DBT\keys\service-account.json"
```

Resultado esperado:

```text
Dataset ready: dbt-exam-project-490202.raw
dbt-exam-project-490202.raw.raw_customers: 10 rows
dbt-exam-project-490202.raw.raw_orders: 15 rows
```

## 8. Ejecutar pipeline dbt

Validar freshness de fuentes:

```powershell
dbt source freshness --profiles-dir "C:\Users\<USUARIO>\Downloads\dbt_202610_codex\profiles"
```

Ejecutar todos los modelos y tests:

```powershell
dbt build --profiles-dir "C:\Users\<USUARIO>\Downloads\dbt_202610_codex\profiles"
```

Resultado esperado:

```text
PASS=15 WARN=1 ERROR=0 SKIP=0 NO-OP=0 TOTAL=16
```

El warning esperado corresponde al test:

```text
no_cancelled_order_with_revenue
```

Ese test esta configurado como warning, por eso no bloquea el pipeline.

## 9. Generar documentacion dbt

Generar docs:

```powershell
dbt docs generate --profiles-dir "C:\Users\<USUARIO>\Downloads\dbt_202610_codex\profiles"
```

Servir docs localmente:

```powershell
dbt docs serve --profiles-dir "C:\Users\<USUARIO>\Downloads\dbt_202610_codex\profiles"
```

Abrir en el navegador:

```text
http://localhost:8080
```

Esta documentacion local sirve para mostrar modelos, sources y lineage del proyecto.

## 10. Validar resultados en BigQuery

En BigQuery, ejecutar:

```sql
SELECT 'raw.raw_customers' AS table_name, COUNT(*) AS rows
FROM `dbt-exam-project-490202.raw.raw_customers`
UNION ALL
SELECT 'raw.raw_orders', COUNT(*)
FROM `dbt-exam-project-490202.raw.raw_orders`
UNION ALL
SELECT 'dbt_dataset.stg_customers', COUNT(*)
FROM `dbt-exam-project-490202.dbt_dataset.stg_customers`
UNION ALL
SELECT 'dbt_dataset.stg_orders', COUNT(*)
FROM `dbt-exam-project-490202.dbt_dataset.stg_orders`
UNION ALL
SELECT 'dbt_dataset.fct_customer_revenue', COUNT(*)
FROM `dbt-exam-project-490202.dbt_dataset.fct_customer_revenue`
UNION ALL
SELECT 'dbt_dataset.fct_revenue_cop', COUNT(*)
FROM `dbt-exam-project-490202.dbt_dataset.fct_revenue_cop`;
```

Consultar tabla final principal:

```sql
SELECT *
FROM `dbt-exam-project-490202.dbt_dataset.fct_customer_revenue`
ORDER BY ingresos_totales DESC
LIMIT 10;
```

Consultar ingresos en COP:

```sql
SELECT *
FROM `dbt-exam-project-490202.dbt_dataset.fct_revenue_cop`
ORDER BY monto_total_cop DESC
LIMIT 10;
```

## 11. Visualizar en Looker Studio

Entrar a:

```text
https://lookerstudio.google.com/
```

Crear dashboard:

1. Clic en `Create`.
2. Clic en `Report`.
3. Seleccionar el conector `BigQuery`.
4. Autorizar la cuenta de Google.
5. Seleccionar:

```text
Project: dbt-exam-project-490202
Dataset: dbt_dataset
Table: fct_customer_revenue
```

6. Clic en `Add` o `Add to report`.

## 12. Graficas recomendadas en Looker Studio

Crear estos elementos:

```text
Scorecard
Metric: ingresos_totales
```

```text
Scorecard
Metric: pedidos_pagados
```

```text
Bar chart
Dimension: ciudad
Metric: ingresos_totales
```

```text
Pie chart
Dimension: canal_registro
Metric: ingresos_totales
```

```text
Table
Dimensions: id_cliente, codigo_pais, ciudad, nivel_cliente
Metrics: ingresos_totales, total_pedidos, pedidos_pagados
```

Agregar una segunda fuente de datos:

1. Menu superior: `Resource`.
2. `Manage added data sources`.
3. `Add a data source`.
4. Seleccionar `BigQuery`.
5. Seleccionar:

```text
Project: dbt-exam-project-490202
Dataset: dbt_dataset
Table: fct_revenue_cop
```

Crear grafica adicional:

```text
Time series o Bar chart
Dimension: fecha_pedido
Metric: monto_total_cop
```

## 13. Que mostrar en el video final

Orden recomendado:

1. Repositorio clonado en VS Code.
2. Ambiente virtual activado.
3. `dbt debug` pasando correctamente.
4. Script de carga raw a BigQuery.
5. `dbt source freshness`.
6. `dbt build`.
7. Tablas creadas en BigQuery.
8. Consultas SQL de validacion.
9. dbt Docs en `localhost:8080`.
10. Dashboard de Looker Studio conectado a BigQuery.

## 14. Problemas comunes

Si `dbt debug` falla por profile:

- Revisar que el profile se llame `dbt_202610`.
- Revisar que `--profiles-dir` apunte a la carpeta donde esta `profiles.yml`.
- Revisar que el `keyfile` exista.

Si Looker Studio no muestra el proyecto:

- La cuenta de Google no tiene permisos sobre BigQuery.
- Pedir acceso al proyecto `dbt-exam-project-490202`.
- Verificar que las tablas existan en `dbt_dataset`.

Si PowerShell bloquea el ambiente virtual:

```powershell
Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass
.\venv\Scripts\Activate.ps1
```

