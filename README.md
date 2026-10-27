# Guía de Ejecución: Academic Enrollment API (Server + Postman)

## 1. Requisitos previos
- **Python 3.x** instalado (no requiere instalar librerías externas).
- **Postman** (versión de escritorio o web).

---

## 2. Cómo levantar el Servidor (Terminal)

1. Abre una terminal (**PowerShell** o **CMD**) en la carpeta del proyecto:
   ```powershell
   cd "D:\Proyectos\Taller - Diseño API"
   ```

2. Ejecuta el servidor local:
   ```powershell
   python server.py
   ```

3. Verás en consola que el servidor queda activo escuchando en `http://localhost:8080/api/v1`:
   ```text
   =================================================================
    ACADEMIC ENROLLMENT API - SERVIDOR DE CONTRATO OPENAPI 3.0.3
    Escuchando en: http://localhost:8080/api/v1
    Presiona Ctrl+C para detener el servidor.
   =================================================================
   ```
   *(Deja esta ventana de terminal abierta; aquí aparecerán los **logs en tiempo real** cada vez que envíes una petición desde Postman).*

---

## 3. Cómo importar y ejecutar en Postman

### Paso 1: Importar la colección
1. Abre **Postman**.
2. Haz clic en el botón **Import** (arriba a la izquierda).
3. Selecciona el archivo **`postman/API.postman_collection.json`** (también puedes importar `openapi.yaml` o `openapi.json`).

### Paso 2: Ejecutar los 4 Requests contra el servidor
Despliega la colección **Academic Enrollment API** en Postman y presiona el botón azul **Send** en cada una de las 4 peticiones:

1. **`1. Registrar Matrícula (POST /enrollments)`**
   - Envía la petición con el botón **Send** → Recibirás **`201 Created`** con la matrícula creada.
   - **Para probar errores (409 / 422):**
     - Cambia `"studentId": "EST-DUPLICADO"` en el Body → Recibirás **`409 Conflict`**.
     - Cambia `"courseCode": "ISWZ-9999"` en el Body → Recibirás **`422 Unprocessable Entity`**.

2. **`2. Consultar Matrícula por ID (GET /enrollments/{enrollmentId})`**
   - Envía la petición con **Send** → Recibirás **`200 OK`** con el detalle de `ENR-2026-8912`.
   - **Para probar error (404):** Cambia el Path Variable `enrollmentId` a `ENR-2026-9999` → Recibirás **`404 Not Found`**.

3. **`3. Buscar Matrículas por Filtros (GET /enrollments?studentId=&periodId=)`**
   - Envía la petición con **Send** → Recibirás **`200 OK`** con la lista de matrículas filtradas.
   - **Para probar error (400):** Desmarca el Query Param `studentId` y presiona **Send** → Recibirás **`400 Bad Request`**.

4. **`4. Modificar Parcialmente Matrícula (PATCH /enrollments/{enrollmentId})`**
   - Envía la petición con **Send** → Recibirás **`200 OK`** con el estado actualizado a `CANCELLED`.
   - **Para probar error (422):** En el Body cambia `"remarks"` para que incluya el texto `"Retiro fuera de plazo"` → Recibirás **`422 Unprocessable Entity`**.

---

## 4. Visualización de Logs en la Terminal

A medida que envíes las peticiones desde Postman, la terminal donde corre `python server.py` mostrará automáticamente los logs con fecha, método HTTP, ruta, código de respuesta y `correlationId`:

```text
[2026-10-27 16:05:10] [HTTP] POST   /api/v1/enrollments -> 201 | Matrícula creada id=ENR-2026-8912 studentId=EST-89421 totalCredits=7
[2026-10-27 16:05:15] [HTTP] GET    /api/v1/enrollments/ENR-2026-8912 -> 200 | Consulta de matrícula id=ENR-2026-8912
[2026-10-27 16:05:22] [HTTP] GET    /api/v1/enrollments?studentId=EST-89421&periodId=2026-1&status=CONFIRMED -> 200 | Búsqueda de matrículas para studentId=EST-89421 (1 resultado)
[2026-10-27 16:05:30] [HTTP] PATCH  /api/v1/enrollments/ENR-2026-8912 -> 200 | Matrícula actualizada id=ENR-2026-8912 nuevoEstado=CANCELLED
[2026-10-27 16:05:40] [HTTP] GET    /api/v1/enrollments/ENR-2026-9999 -> 404 | ERROR ENROLLMENT_NOT_FOUND: No se encontró ningún registro de matrícula con el identificador 'ENR-2026-9999'. | correlationId=3311aa88-22bb-44cc-88dd-998877665544
```
