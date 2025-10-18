import os
import google.genai as genai

PROJECT_ID = os.getenv("PROJECT_ID")
REGION = os.getenv("REGION", "us-central1")

# Set up for Vertex AI mode with ADC - correct environment variables
os.environ["GOOGLE_CLOUD_PROJECT"] = PROJECT_ID
os.environ["GOOGLE_CLOUD_LOCATION"] = REGION 
os.environ["GOOGLE_GENAI_USE_VERTEXAI"] = "true"

# Current available models from documentation
PREFERRED_MODELS = [
    os.getenv("GENAI_MODEL", "gemini-2.5-flash"),
    "gemini-2.0-flash", 
    "gemini-1.5-pro",
    "gemini-1.5-flash",
]

def gen_text(prompt: str) -> str:
    # Use Google Gen AI SDK with Vertex AI backend
    import logging
    
    # Setup logging
    logging.basicConfig(level=logging.INFO)
    logger = logging.getLogger(__name__)
    
    try:
        logger.info(f"Using Google Gen AI SDK with Vertex AI backend")
        logger.info(f"Project: {PROJECT_ID}, Region: {REGION}")
        
        # Initialize Google Gen AI client for Vertex AI backend
        client = genai.Client()
        logger.info("✅ Google Gen AI Client initialized for Vertex AI backend")
        
        # Try models in order of preference
        last_err = None
        for model_name in PREFERRED_MODELS:
            try:
                logger.info(f"🔍 Trying model: {model_name}")
                
                response = client.models.generate_content(
                    model=model_name,
                    contents=[{
                        "role": "user",
                        "parts": [{"text": prompt}]
                    }]
                )
                
                logger.info(f"✅ SUCCESS with model: {model_name}")
                return response.candidates[0].content.parts[0].text
                
            except Exception as e:
                logger.warning(f"❌ Model {model_name} failed: {e}")
                last_err = e
                continue
        
        # All models failed - use fallback templates
        logger.warning("⚠️ All AI models failed, using fallback templates")
        return get_fallback_content(prompt)
        
    except Exception as e:
        logger.error(f"Google Gen AI SDK error: {e}")
        logger.error(f"Error type: {type(e).__name__}")
        return get_fallback_content(prompt)

def get_fallback_content(prompt: str) -> str:
    """Generate fallback content when AI models are unavailable"""
    if "Architecture Decision Record" in prompt:
        return get_fallback_adr(prompt)
    elif "OpenAPI" in prompt:
        return get_fallback_openapi(prompt) 
    else:
        return get_fallback_code(prompt)

def get_fallback_adr(prompt: str) -> str:
    """Fallback ADR template"""
    service_name = "employee-api"  # Extract from prompt if needed
    return f"""# ADR: {service_name}

## Status
Accepted

## Context
Building a secure Employee Management API for Cloud Run deployment.
Region: us-central1. Stack: FastAPI (Python 3.11). Testing: pytest.

## Decision
- **Language**: Python 3.11
- **Framework**: FastAPI
- **Runtime**: Google Cloud Run
- **Database**: In-memory (MVP)
- **Testing**: pytest
- **Security**: JWT-ready scaffolding

## Consequences
- Fast development cycle
- Cloud-native deployment
- Scalable architecture
- Ready for production enhancement
"""

def get_fallback_openapi(prompt: str) -> str:
    """Fallback OpenAPI spec"""
    service_name = "employee-api"
    return f"""openapi: 3.1.0
info:
  title: {service_name.title()}
  version: 1.0.0
  description: Employee Management API
paths:
  /health:
    get:
      summary: Health check
      responses:
        '200':
          description: Service is healthy
          content:
            application/json:
              schema:
                type: object
                properties:
                  status:
                    type: string
                    example: ok
  /employees/{id}:
    get:
      summary: Get employee by ID
      parameters:
        - name: id
          in: path
          required: true
          schema:
            type: integer
      responses:
        '200':
          description: Employee details
          content:
            application/json:
              schema:
                $ref: '#/components/schemas/Employee'
components:
  schemas:
    Employee:
      type: object
      properties:
        id:
          type: integer
        name:
          type: string
        role:
          type: string
"""

def get_fallback_code(prompt: str) -> str:
    """Fallback code generation"""
    return """# app/main.py
from fastapi import FastAPI
from pydantic import BaseModel

app = FastAPI(title="Employee API", version="1.0.0")

class Employee(BaseModel):
    id: int
    name: str
    role: str

EMPLOYEES = {
    1: {"id": 1, "name": "Jane Doe", "role": "Engineer"},
    2: {"id": 2, "name": "John Smith", "role": "Manager"},
}

@app.get("/health")
def health_check():
    return {"status": "ok"}

@app.get("/employees/{emp_id}", response_model=Employee)
def get_employee(emp_id: int):
    employee = EMPLOYEES.get(emp_id)
    if employee:
        return employee
    return {"id": emp_id, "name": "Unknown", "role": "Unknown"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8080)

# app/tests/test_health.py
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def test_health_check():
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}

def test_get_employee():
    response = client.get("/employees/1")
    assert response.status_code == 200
    data = response.json()
    assert data["id"] == 1
    assert data["name"] == "Jane Doe"
"""

def render_template(template_str: str, **kwargs) -> str:
    # Simple string formatting instead of Jinja2
    return template_str.format(**kwargs)

def synthesize(service_name: str, region: str, requirement: str):
    try:
        from orchestrator.prompts import ADR_PROMPT, OPENAPI_PROMPT, CODE_PROMPT
    except ImportError:
        from prompts import ADR_PROMPT, OPENAPI_PROMPT, CODE_PROMPT
    
    adr = gen_text(ADR_PROMPT.format(service_name=service_name, region=region))
    openapi = gen_text(OPENAPI_PROMPT.format(service_name=service_name))
    code = gen_text(CODE_PROMPT.format(service_name=service_name))
    return {"ADR.md": adr, "openapi.yaml": openapi, "__CODE__": code}

def materialize_repo_root(target_dir: str, synthesized: dict, template_dir: str):
    """
    Writes a complete, buildable service into target_dir:
    - ADR.md
    - openapi.yaml
    - requirements.txt (from template)
    - Dockerfile (from template)
    - app/main.py            (from LLM)
    - app/tests/test_health.py (from LLM or fallback)
    """
    os.makedirs(os.path.join(target_dir, "app", "tests"), exist_ok=True)

    # Write ADR & OpenAPI
    with open(os.path.join(target_dir, "ADR.md"), "w") as f:
        f.write(synthesized["ADR.md"])
    with open(os.path.join(target_dir, "openapi.yaml"), "w") as f:
        f.write(synthesized["openapi.yaml"])

    # Split code blob into main + test if possible; fallback to defaults
    code_blob = synthesized["__CODE__"]
    main_code = None
    test_code = None

    if "app/main.py" in code_blob and "app/tests/test_health.py" in code_blob:
        # naive marker split
        after_main = code_blob.split("app/main.py", 1)[1]
        if "app/tests/test_health.py" in after_main:
            main_code, after_test = after_main.split("app/tests/test_health.py", 1)
            test_code = after_test

    if not main_code:
        main_code = """from fastapi import FastAPI
from pydantic import BaseModel

app = FastAPI(title="Generated Service", version="0.1.0")

class Employee(BaseModel):
    id: int
    name: str
    role: str

EMPLOYEES = {1: {"id": 1, "name": "Jane Doe", "role": "Engineer"}}

@app.get("/health")
def health():
    return {"status": "ok"}

@app.get("/employees/{emp_id}", response_model=Employee)
def get_employee(emp_id: int):
    return EMPLOYEES.get(emp_id, {"id": emp_id, "name": "Unknown", "role": "Unknown"})
"""
    if not test_code:
        test_code = """from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def test_health():
    r = client.get("/health")
    assert r.status_code == 200
    assert r.json()["status"] == "ok"
"""

    with open(os.path.join(target_dir, "app", "main.py"), "w") as f:
        f.write(main_code.strip())
    with open(os.path.join(target_dir, "app", "tests", "test_health.py"), "w") as f:
        f.write(test_code.strip())

    # Copy template Dockerfile & requirements
    with open(os.path.join(template_dir, "Dockerfile"), "r") as src, \
         open(os.path.join(target_dir, "Dockerfile"), "w") as dst:
        dst.write(src.read())

    with open(os.path.join(template_dir, "requirements.txt"), "r") as src, \
         open(os.path.join(target_dir, "requirements.txt"), "w") as dst:
        dst.write(src.read())
