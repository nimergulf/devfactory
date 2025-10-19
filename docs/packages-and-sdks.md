# DevFoundry Packages & SDKs

## Complete Technology Stack and Package Justification

This document explains the SDKs and packages chosen for DevFoundry, organized by functional area with justifications for each choice.

---

## 📦 Package Overview

### Installation Structure

```bash
# Production dependencies
pip install -r requirements-full.txt

# Development dependencies  
pip install -r requirements-dev.txt

# Minimal install (orchestrator only)
pip install -r requirements.txt
```

---

## 🏗️ Core Framework Stack

### Web Framework: **FastAPI + Uvicorn**

**Packages**:
- `fastapi==0.104.1`
- `uvicorn[standard]==0.24.0`
- `pydantic==2.5.0`

**Why FastAPI?**
- ✅ **Async-first**: Native async/await support for high concurrency
- ✅ **Auto-documentation**: OpenAPI/Swagger docs generated automatically
- ✅ **Type safety**: Pydantic integration for request/response validation
- ✅ **Performance**: One of the fastest Python frameworks (on par with NodeJS/Go)
- ✅ **Developer experience**: Excellent tooling and IDE support
- ✅ **Dependency injection**: Built-in DI system for clean architecture

**Use in DevFoundry**:
- Orchestrator API endpoints
- Webhook receivers for GitHub/Cloud Build
- Real-time WebSocket connections for UI
- Health checks and monitoring endpoints

**Alternatives Considered**:
- ❌ Flask: Synchronous by default, requires extensions
- ❌ Django: Too heavy for microservices, batteries-included approach
- ❌ Sanic: Less mature ecosystem, smaller community

---

## ☁️ Google Cloud Platform (GCP) Integration

### Core GCP SDKs

#### 1. Vertex AI: **google-cloud-aiplatform**

**Package**: `google-cloud-aiplatform==1.38.0`

**Purpose**: Primary LLM access for all agents

**Key Features**:
- Gemini Pro/Ultra model access
- PaLM 2 models (legacy support)
- Model Garden access for specialized models
- Fine-tuning capabilities
- Batch prediction support
- Model evaluation and monitoring

**Usage Example**:
```python
from google.cloud import aiplatform
from vertexai.preview.generative_models import GenerativeModel

# Initialize Vertex AI
aiplatform.init(project="devfoundry-platform", location="us-central1")

# Use Gemini Pro
model = GenerativeModel("gemini-pro")
response = model.generate_content("Analyze this architecture...")
```

**Cost Optimization**:
- Use `gemini-flash` for simple tasks (10x cheaper)
- Cache frequently used prompts
- Implement request batching

#### 2. Cloud Storage: **google-cloud-storage**

**Package**: `google-cloud-storage==2.10.0`

**Purpose**: Artifact storage (code, IaC, docs, SBOMs)

**Key Features**:
- Object versioning for artifact history
- Signed URLs for secure downloads
- Lifecycle policies for cost management
- Transfer acceleration for large files
- Server-side encryption

**Usage Pattern**:
```python
from google.cloud import storage

client = storage.Client()
bucket = client.bucket("devfoundry-artifacts")

# Upload artifact with metadata
blob = bucket.blob(f"workflows/{workflow_id}/code.zip")
blob.metadata = {"workflow_id": workflow_id, "stage": "development"}
blob.upload_from_filename("generated_code.zip")

# Generate signed URL (valid for 1 hour)
signed_url = blob.generate_signed_url(expiration=3600)
```

#### 3. Firestore: **google-cloud-firestore**

**Package**: `google-cloud-firestore==2.13.1`

**Purpose**: Workflow state, metadata, audit logs

**Why Firestore?**
- ✅ Real-time synchronization for UI updates
- ✅ ACID transactions for workflow consistency
- ✅ Automatic indexing
- ✅ Offline support for CLI
- ✅ Scalable to millions of operations

**Data Model**:
```python
from google.cloud import firestore

db = firestore.Client()

# Workflow collection
workflow_ref = db.collection('workflows').document(workflow_id)
workflow_ref.set({
    'status': 'in_progress',
    'created_at': firestore.SERVER_TIMESTAMP,
    'agents_completed': [],
    'current_stage': 'architecture'
})

# Real-time listener for UI
def on_snapshot(doc_snapshot, changes, read_time):
    for doc in doc_snapshot:
        print(f"Workflow status: {doc.to_dict()['status']}")

workflow_ref.on_snapshot(on_snapshot)
```

#### 4. Secret Manager: **google-cloud-secret-manager**

**Package**: `google-cloud-secret-manager==2.16.4`

**Purpose**: API keys, credentials, certificates

**Security Best Practices**:
```python
from google.cloud import secretmanager

client = secretmanager.SecretManagerServiceClient()

# Access secret
name = f"projects/{project_id}/secrets/vertex-ai-key/versions/latest"
response = client.access_secret_version(request={"name": name})
api_key = response.payload.data.decode('UTF-8')

# Automatic rotation support
# Secrets can be versioned and rotated without code changes
```

#### 5. Cloud Build: **google-cloud-build**

**Package**: `google-cloud-build==3.20.0`

**Purpose**: Trigger CI/CD pipelines, monitor builds

**Integration**:
```python
from google.cloud.devtools import cloudbuild_v1

client = cloudbuild_v1.CloudBuildClient()

# Trigger build
build = cloudbuild_v1.Build()
build.source.repo_source.repo_name = "devfoundry-generated"
build.source.repo_source.branch_name = "main"

operation = client.create_build(project_id=project_id, build=build)
result = operation.result()  # Wait for completion
```

#### 6. Pub/Sub: **google-cloud-pubsub**

**Package**: `google-cloud-pubsub==2.18.4`

**Purpose**: Agent event streaming, async communication

**Event-Driven Architecture**:
```python
from google.cloud import pubsub_v1

publisher = pubsub_v1.PublisherClient()
topic_path = publisher.topic_path(project_id, "agent-events")

# Publish agent completion event
data = json.dumps({
    "workflow_id": workflow_id,
    "agent": "DeveloperAgent",
    "status": "completed",
    "artifacts": ["source_code", "tests"]
}).encode("utf-8")

future = publisher.publish(topic_path, data)
message_id = future.result()
```

---

## 🤖 Workflow Orchestration

### Choice: **Temporal**

**Package**: `temporalio==1.5.0`

**Why Temporal?**
- ✅ **Durable execution**: Workflows survive process crashes
- ✅ **Visual debugging**: Timeline view of workflow execution
- ✅ **Automatic retries**: Built-in error handling with backoff
- ✅ **Versioning**: Deploy new workflow versions without breaking running instances
- ✅ **Child workflows**: Compose complex agent graphs
- ✅ **Signals/queries**: Real-time interaction with running workflows

**Workflow Definition Example**:
```python
from temporalio import workflow, activity
from datetime import timedelta

@workflow.defn
class DevFoundryWorkflow:
    @workflow.run
    async def run(self, concept: str) -> dict:
        # Stage 1: Conceptualize
        requirements = await workflow.execute_activity(
            analyze_concept,
            concept,
            start_to_close_timeout=timedelta(minutes=5)
        )
        
        # Stage 2: Architecture (parallel agents)
        arch_tasks = [
            workflow.execute_activity(architect_agent, requirements),
            workflow.execute_activity(api_agent, requirements)
        ]
        arch_results = await asyncio.gather(*arch_tasks)
        
        # Stage 3: Development
        code = await workflow.execute_activity(
            developer_agent,
            arch_results,
            start_to_close_timeout=timedelta(minutes=30)
        )
        
        return {"status": "completed", "artifacts": code}
```

**Alternatives Considered**:
- **Celery**: Simpler but lacks durable execution and complex workflow support
- **Apache Airflow**: Designed for data pipelines, overkill for our use case
- **AWS Step Functions**: Vendor lock-in, less flexible than Temporal

---

## 🧠 AI/LLM Integration

### Multi-Model Strategy

**Primary: Vertex AI (Gemini)**
- `google-generativeai==0.3.1`
- `langchain-google-vertexai==0.0.4`

**Fallback: OpenAI (GPT-4)**
- `openai==1.3.5`

**Future: Anthropic (Claude)**
- `anthropic==0.7.1`

### LangChain for Orchestration

**Package**: `langchain==0.0.350`

**Why LangChain?**
- ✅ **Prompt templates**: Reusable, parameterized prompts
- ✅ **Output parsers**: Structured output extraction (JSON, Pydantic)
- ✅ **Memory**: Conversation history management
- ✅ **Chains**: Compose multi-step LLM interactions
- ✅ **Model routing**: Switch between models transparently

**Agent Prompt Pattern**:
```python
from langchain.prompts import PromptTemplate
from langchain.output_parsers import PydanticOutputParser
from pydantic import BaseModel, Field

class ArchitectureOutput(BaseModel):
    style: str = Field(description="Architecture style (microservice, monolith, etc)")
    components: list[str] = Field(description="List of components")
    adrs: list[dict] = Field(description="Architecture Decision Records")

parser = PydanticOutputParser(pydantic_object=ArchitectureOutput)

prompt = PromptTemplate(
    template="""You are a Senior Software Architect.
    
    Requirements: {requirements}
    
    Design an architecture following best practices.
    
    {format_instructions}
    """,
    input_variables=["requirements"],
    partial_variables={"format_instructions": parser.get_format_instructions()}
)

# Use with any LLM
from langchain_google_vertexai import VertexAI
llm = VertexAI(model_name="gemini-pro")
chain = prompt | llm | parser
result = chain.invoke({"requirements": requirements})
```

### Token Management

**Package**: `tiktoken==0.5.1`

**Purpose**: Count tokens to optimize costs and avoid limits

```python
import tiktoken

encoding = tiktoken.get_encoding("cl100k_base")  # For GPT-4
tokens = encoding.encode(prompt_text)

if len(tokens) > 8000:
    # Truncate or summarize
    pass
```

---

## 🔐 Security & Compliance

### SBOM Generation

**Packages**:
- `cyclonedx-python-lib==5.1.1` - CycloneDX format (OWASP standard)
- `syft-py==0.1.0` - Anchore Syft wrapper

**Usage**:
```python
from cyclonedx.model import bom
from cyclonedx.model.component import Component

# Generate SBOM
bom_obj = bom.Bom()
component = Component(
    name="fastapi",
    version="0.104.1",
    component_type="library"
)
bom_obj.components.add(component)

# Export to JSON
from cyclonedx.output import OutputFormat, get_instance
outputter = get_instance(bom_obj, OutputFormat.JSON)
print(outputter.output_as_string())
```

### Vulnerability Scanning

**Packages**:
- `safety==2.3.5` - Python dependency vulnerabilities
- `grype-py==0.1.0` - Container and package scanning
- `bandit==1.7.5` - Python code security linter

**Pipeline Integration**:
```python
import subprocess

# Scan dependencies
result = subprocess.run(['safety', 'check', '--json'], capture_output=True)
vulnerabilities = json.loads(result.stdout)

# Scan code
result = subprocess.run(['bandit', '-r', 'orchestrator/', '-f', 'json'], capture_output=True)
security_issues = json.loads(result.stdout)

# Fail if high severity found
if any(v['severity'] == 'high' for v in vulnerabilities):
    raise SecurityError("High severity vulnerabilities detected")
```

### Static Analysis (SAST)

**Package**: `semgrep==1.45.0`

**Why Semgrep?**
- ✅ Multi-language support
- ✅ Custom rule creation
- ✅ Fast execution
- ✅ CI/CD integration
- ✅ OWASP Top 10 rules built-in

```bash
# Run Semgrep with OWASP rules
semgrep --config=p/owasp-top-ten orchestrator/
```

---

## 🧪 Testing Framework

### Pytest Ecosystem

**Core**:
- `pytest==7.4.3` - Testing framework
- `pytest-asyncio==0.21.1` - Async test support
- `pytest-cov==4.1.0` - Coverage reporting
- `pytest-xdist==3.5.0` - Parallel execution

**Enhanced Testing**:
- `pytest-mock==3.12.0` - Mocking utilities
- `faker==20.1.0` - Test data generation
- `factory-boy==3.3.0` - Test fixtures
- `hypothesis==6.92.1` - Property-based testing

**Test Structure**:
```python
import pytest
from hypothesis import given, strategies as st
from faker import Faker

fake = Faker()

class TestDeveloperAgent:
    @pytest.fixture
    def agent(self):
        return DeveloperAgent()
    
    def test_basic_code_generation(self, agent):
        result = agent.generate_code(api_spec)
        assert result.status == "success"
    
    @pytest.mark.asyncio
    async def test_async_generation(self, agent):
        result = await agent.async_generate(spec)
        assert "main.py" in result.files
    
    @given(st.text(min_size=10), st.integers(min_value=1, max_value=100))
    def test_property_based(self, concept, max_features):
        # Test that any valid input produces valid output
        result = agent.extract_features(concept, max_features)
        assert len(result) <= max_features
    
    def test_with_fake_data(self):
        email = fake.email()
        name = fake.name()
        user = create_user(email, name)
        assert user.email == email
```

---

## 📊 Observability & Monitoring

### Structured Logging

**Package**: `structlog==23.2.0`

**Why Structured Logging?**
- ✅ Machine-readable logs (JSON)
- ✅ Automatic context injection
- ✅ Performance-optimized
- ✅ GCP Logging integration

```python
import structlog

log = structlog.get_logger()

# Automatic context binding
log = log.bind(workflow_id=workflow_id, agent="DeveloperAgent")

# Structured logging
log.info("agent_started", 
         stage="development",
         estimated_duration=300)

log.error("agent_failed",
          error_type="ValidationError",
          retry_count=3)
```

### OpenTelemetry Integration

**Packages**:
- `opentelemetry-api==1.21.0`
- `opentelemetry-sdk==1.21.0`
- `opentelemetry-instrumentation-fastapi==0.42b0`
- `opentelemetry-exporter-gcp-trace==1.6.0`

**Distributed Tracing**:
```python
from opentelemetry import trace
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor
from opentelemetry.exporter.cloud_trace import CloudTraceSpanExporter

# Setup tracing
trace.set_tracer_provider(TracerProvider())
tracer = trace.get_tracer(__name__)

# Trace agent execution
with tracer.start_as_current_span("developer_agent"):
    with tracer.start_as_current_span("generate_code"):
        code = generate_code(spec)
    with tracer.start_as_current_span("run_tests"):
        test_results = run_tests(code)
```

### Prometheus Metrics

**Package**: `prometheus-client==0.19.0`

**Custom Metrics**:
```python
from prometheus_client import Counter, Histogram, Gauge

# Track agent executions
agent_executions = Counter(
    'devfoundry_agent_executions_total',
    'Total agent executions',
    ['agent_name', 'status']
)

# Track execution time
agent_duration = Histogram(
    'devfoundry_agent_duration_seconds',
    'Agent execution duration',
    ['agent_name']
)

# Track active workflows
active_workflows = Gauge(
    'devfoundry_active_workflows',
    'Number of active workflows'
)

# Usage
with agent_duration.labels(agent_name="DeveloperAgent").time():
    result = agent.execute()
    agent_executions.labels(
        agent_name="DeveloperAgent",
        status="success"
    ).inc()
```

---

## 🔄 Async & Concurrency

### HTTP Clients

**Package**: `httpx==0.25.2`

**Why HTTPX over requests?**
- ✅ Async support
- ✅ HTTP/2 support
- ✅ Connection pooling
- ✅ Request timeout handling
- ✅ Automatic retries

```python
import httpx
from tenacity import retry, stop_after_attempt, wait_exponential

@retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=4, max=10))
async def call_external_api(url: str, data: dict):
    async with httpx.AsyncClient(timeout=30.0) as client:
        response = await client.post(url, json=data)
        response.raise_for_status()
        return response.json()
```

### File Operations

**Package**: `aiofiles==23.2.1`

**Async File I/O**:
```python
import aiofiles

async def save_artifacts(workflow_id: str, files: dict):
    tasks = []
    for filename, content in files.items():
        tasks.append(save_file(filename, content))
    await asyncio.gather(*tasks)

async def save_file(filename: str, content: str):
    async with aiofiles.open(f"artifacts/{filename}", 'w') as f:
        await f.write(content)
```

---

## 🎨 CLI Development

### Rich Terminal UI

**Package**: `rich==13.7.0`

**Beautiful CLI Output**:
```python
from rich.console import Console
from rich.progress import Progress, SpinnerColumn, TextColumn
from rich.table import Table

console = Console()

# Progress bars
with Progress(
    SpinnerColumn(),
    TextColumn("[progress.description]{task.description}"),
    console=console
) as progress:
    task = progress.add_task("[cyan]Generating code...", total=100)
    # Update progress
    progress.update(task, advance=20)

# Tables
table = Table(title="Generated Artifacts")
table.add_column("Type", style="cyan")
table.add_column("File", style="green")
table.add_column("Size", justify="right")

table.add_row("Code", "main.py", "15 KB")
table.add_row("Tests", "test_main.py", "8 KB")
console.print(table)

# Pretty JSON
console.print_json(data={"status": "completed"})
```

### Interactive Prompts

**Package**: `questionary==2.0.1`

**User Input**:
```python
import questionary

# Select from options
architecture = questionary.select(
    "Choose architecture style:",
    choices=["Microservice", "Monolith", "Serverless", "Event-Driven"]
).ask()

# Multi-select
compliance = questionary.checkbox(
    "Select compliance frameworks:",
    choices=["ISO 27001", "SOC 2", "HIPAA", "PCI DSS", "GDPR"]
).ask()

# Confirmation
if questionary.confirm("Deploy to production?").ask():
    deploy_to_production()
```

---

## 📦 Package Management Strategy

### Requirements Organization

```
requirements.txt              # Minimal (orchestrator only)
requirements-full.txt         # Production complete
requirements-dev.txt          # Development tools
requirements-agents.txt       # Agent-specific dependencies
requirements-security.txt     # Security scanning tools
requirements-docs.txt         # Documentation generation
```

### Dependency Pinning

**Strategy**:
- Pin major + minor versions for stability
- Allow patch updates for security fixes
- Use `pip-tools` for dependency compilation

```bash
# Compile requirements
pip-compile requirements.in --output-file requirements.txt

# Upgrade all to latest compatible
pip-compile --upgrade requirements.in

# Sync environment
pip-sync requirements.txt
```

### Dependency Scanning

```bash
# Check for vulnerabilities
safety check

# Audit all dependencies
pip-audit

# Check for outdated packages
pip list --outdated

# Visualize dependency tree
pipdeptree
```

---

## 🚀 Performance Optimization

### Caching

**Packages**:
- `redis==5.0.1` - Distributed cache
- `diskcache==5.6.3` - Local disk cache
- `cachetools==5.3.2` - Memory cache with TTL

**Multi-Level Caching**:
```python
from cachetools import TTLCache, cached
from functools import lru_cache
import redis

# Memory cache (process-level)
memory_cache = TTLCache(maxsize=1000, ttl=300)

@cached(cache=memory_cache)
def get_template(template_name: str):
    return load_template_from_disk(template_name)

# Redis cache (distributed)
redis_client = redis.Redis(host='localhost', port=6379)

def get_architecture_pattern(pattern_name: str):
    # Try cache first
    cached = redis_client.get(f"pattern:{pattern_name}")
    if cached:
        return json.loads(cached)
    
    # Generate and cache
    pattern = generate_pattern(pattern_name)
    redis_client.setex(
        f"pattern:{pattern_name}",
        3600,  # 1 hour TTL
        json.dumps(pattern)
    )
    return pattern
```

---

## 📖 Documentation Generation

### API Documentation

**Package**: `mkdocs-material==9.4.14`

**Why MkDocs Material?**
- ✅ Beautiful, modern theme
- ✅ Search built-in
- ✅ Mobile responsive
- ✅ Code highlighting
- ✅ Automatic nav generation

```yaml
# mkdocs.yml
site_name: DevFoundry Documentation
theme:
  name: material
  features:
    - navigation.tabs
    - navigation.sections
    - toc.integrate
    - search.suggest

plugins:
  - search
  - mkdocstrings:
      handlers:
        python:
          options:
            show_source: true
```

---

## 🎯 Summary: Package Selection Criteria

For every package in DevFoundry, we evaluated:

1. **Maturity**: Active maintenance, stable releases
2. **Performance**: Benchmarked against alternatives
3. **Community**: GitHub stars, downloads, Stack Overflow questions
4. **Documentation**: Quality and completeness
5. **GCP Integration**: Native support or easy integration
6. **Type Safety**: Python type hints support
7. **Async Support**: First-class async/await
8. **Testing**: Well-tested, high coverage
9. **Security**: No known vulnerabilities
10. **License**: Compatible with enterprise use (Apache, MIT, BSD)

---

## 📊 Package Statistics

| Category | # of Packages | Key Technologies |
|----------|---------------|------------------|
| GCP Integration | 13 | Vertex AI, Firestore, Cloud Run |
| AI/LLM | 6 | LangChain, OpenAI, Anthropic |
| Testing | 15 | Pytest ecosystem |
| Security | 10 | Semgrep, Safety, Bandit |
| Observability | 8 | OpenTelemetry, Structlog |
| Orchestration | 1 | Temporal |
| Code Quality | 8 | Black, Flake8, MyPy |
| **Total Production** | **~80** | **Multi-layered stack** |
| **Total Development** | **~40** | **Enhanced DX** |

---

**Document Version**: 1.0  
**Last Updated**: October 2024  
**Maintained By**: DevFoundry Platform Team
