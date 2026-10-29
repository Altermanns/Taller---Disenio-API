from http.server import HTTPServer, BaseHTTPRequestHandler
from urllib.parse import urlparse, parse_qs
from datetime import datetime, timezone
import json
import uuid

HOST = "localhost"
PORT = 8080

COURSE_CATALOG = {
    "ISWZ-3104": "Integración de Sistemas",
    "ISWZ-3105": "Arquitectura de Software",
}

def now_iso():
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")

def log_event(method, path, status_code, detail, correlation_id=None):
    ts = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    cid_str = f" | correlationId={correlation_id}" if correlation_id else ""
    print(f"[{ts}] [HTTP] {method:6} {path} -> {status_code} | {detail}{cid_str}", flush=True)

class EnrollmentAPIHandler(BaseHTTPRequestHandler):
    def log_message(self, format, *args):
        # Silenciar el log por defecto para usar nuestro log estructurado
        pass

    def _send_json(self, status_code, payload, headers=None):
        body = json.dumps(payload, indent=2, ensure_ascii=False).encode("utf-8")
        self.send_response(status_code)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        if headers:
            for k, v in headers.items():
                self.send_header(k, v)
        self.end_headers()
        self.wfile.write(body)

    def _send_error_model(self, status_code, code, message):
        cid = str(uuid.uuid4())
        payload = {
            "code": code,
            "message": message,
            "correlationId": cid,
            "timestamp": now_iso()
        }
        log_event(self.command, self.path, status_code, f"ERROR {code}: {message}", cid)
        self._send_json(status_code, payload)

    def _read_json_body(self):
        length = int(self.headers.get("Content-Length", 0))
        if length == 0:
            return None
        raw = self.rfile.read(length).decode("utf-8")
        try:
            return json.loads(raw)
        except json.JSONDecodeError:
            return None

    def _normalize_path(self, raw_path):
        if raw_path.startswith("/api/v1/"):
            return raw_path
        if raw_path == "/enrollments" or raw_path.startswith("/enrollments/"):
            return f"/api/v1{raw_path}"
        return raw_path

    def do_POST(self):
        parsed = urlparse(self.path)
        path = self._normalize_path(parsed.path)
        if path != "/api/v1/enrollments":
            return self._send_error_model(404, "ENDPOINT_NOT_FOUND", f"La ruta '{parsed.path}' no existe.")

        data = self._read_json_body()
        if not data or not isinstance(data, dict):
            return self._send_error_model(400, "INVALID_REQUEST_PAYLOAD", "El cuerpo de la solicitud debe ser un JSON válido.")

        student_id = data.get("studentId")
        period_id = data.get("periodId")
        courses = data.get("courses")

        if not student_id or not str(student_id).startswith("EST-"):
            return self._send_error_model(
                400,
                "INVALID_REQUEST_PAYLOAD",
                "El campo 'studentId' es obligatorio y debe tener el formato EST-XXXXX."
            )

        if not period_id or not courses or not isinstance(courses, list):
            return self._send_error_model(
                400,
                "INVALID_REQUEST_PAYLOAD",
                "Los campos 'periodId' y la lista 'courses' (mínimo 1 curso) son obligatorios."
            )

        if student_id == "EST-DUPLICADO":
            return self._send_error_model(
                409,
                "DUPLICATE_ENROLLMENT",
                f"El estudiante {student_id} ya cuenta con una matrícula registrada y activa para el período {period_id}."
            )

        for c in courses:
            if c.get("courseCode") == "ISWZ-9999":
                return self._send_error_model(
                    422,
                    "PREREQUISITE_NOT_MET",
                    "El estudiante no cumple con el prerrequisito para la asignatura ISWZ-9999."
                )

        detailed_courses = []
        total_credits = 0
        for c in courses:
            code = c.get("courseCode", "ISWZ-0000")
            credits = int(c.get("credits", 3))
            total_credits += credits
            detailed_courses.append({
                "courseCode": code,
                "courseName": COURSE_CATALOG.get(code, "Asignatura Universitaria"),
                "group": c.get("group", "G1"),
                "credits": credits
            })

        enrollment_id = "ENR-2026-8912"
        response = {
            "id": enrollment_id,
            "studentId": student_id,
            "periodId": period_id,
            "status": "CONFIRMED",
            "totalCredits": total_credits,
            "registeredAt": "2026-02-15T09:30:00Z",
            "courses": detailed_courses
        }
        log_event("POST", self.path, 201, f"Matrícula creada id={enrollment_id} studentId={student_id} totalCredits={total_credits}")
        self._send_json(201, response, headers={"Location": f"/api/v1/enrollments/{enrollment_id}"})

    def do_GET(self):
        parsed = urlparse(self.path)
        path = self._normalize_path(parsed.path)

        # 1. GET /api/v1/enrollments?studentId=...&periodId=...
        if path == "/api/v1/enrollments":
            query = parse_qs(parsed.query)
            student_id = query.get("studentId", [None])[0]
            period_id = query.get("periodId", ["2026-1"])[0]
            status = query.get("status", ["CONFIRMED"])[0]

            if not student_id:
                return self._send_error_model(
                    400,
                    "MISSING_REQUIRED_QUERY_PARAM",
                    "El parámetro de consulta 'studentId' es obligatorio para realizar la búsqueda."
                )

            response = [
                {
                    "id": "ENR-2026-8912",
                    "studentId": student_id,
                    "periodId": period_id,
                    "status": status,
                    "totalCredits": 7,
                    "registeredAt": "2026-02-15T09:30:00Z",
                    "courses": [
                        {
                            "courseCode": "ISWZ-3104",
                            "courseName": "Integración de Sistemas",
                            "group": "G1",
                            "credits": 3
                        },
                        {
                            "courseCode": "ISWZ-3105",
                            "courseName": "Arquitectura de Software",
                            "group": "G2",
                            "credits": 4
                        }
                    ]
                }
            ]
            log_event("GET", self.path, 200, f"Búsqueda de matrículas para studentId={student_id} (1 resultado)")
            return self._send_json(200, response)

        # 2. GET /api/v1/enrollments/{enrollmentId}
        if path.startswith("/api/v1/enrollments/"):
            enrollment_id = path.split("/api/v1/enrollments/", 1)[1]
            if not enrollment_id.startswith("ENR-"):
                return self._send_error_model(
                    400,
                    "INVALID_IDENTIFIER_FORMAT",
                    "El parámetro de ruta 'enrollmentId' debe cumplir el formato ENR-AAAA-XXXX."
                )
            if enrollment_id == "ENR-2026-9999":
                return self._send_error_model(
                    404,
                    "ENROLLMENT_NOT_FOUND",
                    f"No se encontró ningún registro de matrícula con el identificador '{enrollment_id}'."
                )

            response = {
                "id": enrollment_id,
                "studentId": "EST-89421",
                "periodId": "2026-1",
                "status": "CONFIRMED",
                "totalCredits": 7,
                "registeredAt": "2026-02-15T09:30:00Z",
                "courses": [
                    {
                        "courseCode": "ISWZ-3104",
                        "courseName": "Integración de Sistemas",
                        "group": "G1",
                        "credits": 3
                    },
                    {
                        "courseCode": "ISWZ-3105",
                        "courseName": "Arquitectura de Software",
                        "group": "G2",
                        "credits": 4
                    }
                ]
            }
            log_event("GET", self.path, 200, f"Consulta de matrícula id={enrollment_id}")
            return self._send_json(200, response)

        return self._send_error_model(404, "ENDPOINT_NOT_FOUND", f"La ruta '{path}' no existe.")

    def do_PATCH(self):
        parsed = urlparse(self.path)
        path = self._normalize_path(parsed.path)

        if not path.startswith("/api/v1/enrollments/"):
            return self._send_error_model(404, "ENDPOINT_NOT_FOUND", f"La ruta '{path}' no existe.")

        enrollment_id = path.split("/api/v1/enrollments/", 1)[1]
        if enrollment_id == "ENR-2026-9999":
            return self._send_error_model(
                404,
                "ENROLLMENT_NOT_FOUND",
                f"No se encontró ningún registro de matrícula con el identificador '{enrollment_id}'."
            )

        data = self._read_json_body()
        if not data or not any(k in data for k in ("status", "remarks", "courses")):
            return self._send_error_model(
                400,
                "INVALID_UPDATE_PAYLOAD",
                "No se proporcionó ningún campo modificable válido en la solicitud."
            )

        remarks = str(data.get("remarks", "")).lower()
        if "fuera de plazo" in remarks:
            return self._send_error_model(
                422,
                "DEADLINE_EXCEEDED",
                "El periodo de adición y retiro de materias ha finalizado para el ciclo 2026-1."
            )

        new_status = data.get("status", "CANCELLED")
        response = {
            "id": enrollment_id,
            "studentId": "EST-89421",
            "periodId": "2026-1",
            "status": new_status,
            "totalCredits": 0 if new_status == "CANCELLED" else 7,
            "registeredAt": "2026-02-15T09:30:00Z",
            "courses": [] if new_status == "CANCELLED" else data.get("courses", [])
        }
        log_event("PATCH", self.path, 200, f"Matrícula actualizada id={enrollment_id} nuevoEstado={new_status}")
        return self._send_json(200, response)

if __name__ == "__main__":
    server = HTTPServer((HOST, PORT), EnrollmentAPIHandler)
    print("=" * 65)
    print(" ACADEMIC ENROLLMENT API - SERVIDOR DE CONTRATO OPENAPI 3.0.3")
    print(f" Escuchando en: http://{HOST}:{PORT}/api/v1")
    print(" Presiona Ctrl+C para detener el servidor.")
    print("=" * 65, flush=True)
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\n[INFO] Servidor detenido.")
        server.server_close()
