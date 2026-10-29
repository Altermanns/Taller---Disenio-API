# Academic Enrollment API - Guía de Ejecución

**Autores:**
- ARELLANO BRANDON
- GUALOTO ROMEL
- OLIVO PAULO
- TRUJILLO ISAAC

---

## 1. Levantar el Servidor de Pruebas (Terminal)

Abre una terminal en la carpeta raíz del proyecto (donde se encuentran `openapi.yaml` y `server.py`) y ejecuta **una** de las siguientes opciones:

### Opción A: Servidor Python (incluye validaciones de negocio y logs)
```powershell
python server.py
```

### Opción B: Servidor Mock con Stoplight Prism
```powershell
npx -y @stoplight/prism-cli mock openapi.yaml -p 8080
```

El servidor quedará escuchando en: `http://localhost:8080/api/v1` (también soporta peticiones en `http://localhost:8080`).

---

## 2. Ejecutar Pruebas en Postman

### Paso 1: Importar la colección
1. Abre **Postman**.
2. Haz clic en **Import**.
3. Selecciona el archivo **`postman/API.postman_collection.json`**.

### Paso 2: Probar los Endpoints
Abre la colección **Academic Enrollment API** y presiona **Send** en cada una de las 4 peticiones:

1. **Registrar Matrícula (`POST /enrollments`)**
   - **Éxito (`201 Created`):** Envía el cuerpo por defecto.
   - **Error `409 Conflict`:** En `server.py`, cambia `"studentId"` a `"EST-DUPLICADO"` (o en Prism agrega el header `Prefer: code=409`).
   - **Error `422 Unprocessable Entity`:** En `server.py`, cambia `"courseCode"` a `"ISWZ-9999"` (o en Prism agrega el header `Prefer: code=422`).

2. **Consultar Matrícula por ID (`GET /enrollments/{enrollmentId}`)**
   - **Éxito (`200 OK`):** Envía con `enrollmentId` = `ENR-2026-8912`.
   - **Error `404 Not Found`:** En `server.py`, cambia `enrollmentId` a `ENR-2026-9999` (o en Prism agrega el header `Prefer: code=404`).

3. **Buscar Matrículas por Filtros (`GET /enrollments?studentId=&periodId=`)**
   - **Éxito (`200 OK`):** Envía con los parámetros por defecto (`studentId=EST-89421`).
   - **Error `400 Bad Request`:** Desmarca el parámetro obligatorio `studentId` y envía la petición.

4. **Modificar Parcialmente Matrícula (`PATCH /enrollments/{enrollmentId}`)**
   - **Éxito (`200 OK`):** Envía el cuerpo por defecto (`"status": "CANCELLED"`).
   - **Error `422 Unprocessable Entity`:** En `server.py`, incluye `"fuera de plazo"` en el campo `"remarks"` (o en Prism agrega el header `Prefer: code=422`).
