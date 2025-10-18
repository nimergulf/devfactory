ADR_PROMPT = """You are an expert software architect.
Write an Architecture Decision Record (ADR) for a microservice called "{service_name}".
Context: Build a secure Employee Management API. Region: {region}. Runtime: Cloud Run. CI: Cloud Build.
Stack: FastAPI (Python 3.11). Testing: pytest. Security: JWT ready (future).
Decide on: language, framework, runtime, endpoints, non-functionals, logging, monitoring.
Output as Markdown with sections: Title, Status, Context, Decision, Consequences.
"""

OPENAPI_PROMPT = """You are an expert API designer.
Produce an OpenAPI 3.1 YAML for microservice "{service_name}" with basePath "/".
Endpoints:
- GET /health -> 200 JSON with status field set to "ok"
- GET /employees/{{id}} -> 200 JSON with fields: id:int, name:string, role:string
Ensure proper components/schemas and examples.
"""

CODE_PROMPT = """You are a senior Python engineer.
Generate minimal but production-ready FastAPI code for service "{service_name}" with:
- GET /health -> returns status ok
- GET /employees/{{id}} -> returns from in-memory dict; unknown -> placeholder with Unknown
Write code into 'app/main.py' and a pytest 'app/tests/test_health.py'. Use pydantic BaseModel.
The service must bind on 0.0.0.0:8080 for Cloud Run.
"""
