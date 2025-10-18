"""
DevFactory Orchestrator - Main Service
Enterprise AI-Powered Microservice Generation Platform
"""
import os
import logging
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import Optional, Dict, Any

from orchestrator.graph.workflow import WorkflowOrchestrator
from orchestrator.providers.llm.vertex import VertexAIProvider
from orchestrator.providers.vcs.github import GitHubProvider
from orchestrator.providers.ci.cloudbuild import CloudBuildProvider
from orchestrator.security.scanner import SecurityScanner
from orchestrator.persistence.runs import RunManager

# Configuration
PROJECT_ID = os.getenv("PROJECT_ID")
REGION = os.getenv("REGION", "us-central1")
GITHUB_OWNER = os.getenv("GITHUB_OWNER")
GITHUB_REPO = os.getenv("GITHUB_REPO")
GITHUB_BRANCH = os.getenv("GITHUB_BRANCH", "main")

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(
    title="DevFactory Orchestrator",
    description="Enterprise AI-Powered Microservice Generation Platform",
    version="2.0.0"
)

# Initialize providers and services
workflow_orchestrator = WorkflowOrchestrator()
llm_provider = VertexAIProvider(project_id=PROJECT_ID, region=REGION)
vcs_provider = GitHubProvider(owner=GITHUB_OWNER, repo=GITHUB_REPO, branch=GITHUB_BRANCH)
ci_provider = CloudBuildProvider(project_id=PROJECT_ID)
security_scanner = SecurityScanner()
run_manager = RunManager()

class GenerationRequest(BaseModel):
    service_name: str
    requirement: str
    architecture_type: Optional[str] = "microservice"
    deployment_target: Optional[str] = "cloud-run"
    security_level: Optional[str] = "standard"
    metadata: Optional[Dict[str, Any]] = {}

class GenerationResponse(BaseModel):
    success: bool
    run_id: str
    message: str
    repository_url: Optional[str] = None
    deployment_status: Optional[str] = None
    estimated_completion: Optional[str] = None
    artifacts: Optional[Dict[str, str]] = {}

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "ok",
        "service": "devfactory-orchestrator",
        "version": "2.0.0"
    }

@app.post("/generate", response_model=GenerationResponse)
async def generate_service(request: GenerationRequest):
    """
    Generate a complete microservice from requirements
    """
    try:
        logger.info(f"🎯 Starting service generation for: {request.service_name}")
        
        # Create a new run
        run_id = await run_manager.create_run(
            service_name=request.service_name,
            request_data=request.dict()
        )
        
        # Execute the workflow
        workflow_result = await workflow_orchestrator.execute_generation_workflow(
            run_id=run_id,
            service_name=request.service_name,
            requirement=request.requirement,
            architecture_type=request.architecture_type,
            deployment_target=request.deployment_target,
            security_level=request.security_level,
            metadata=request.metadata,
            providers={
                "llm": llm_provider,
                "vcs": vcs_provider,
                "ci": ci_provider,
                "security": security_scanner
            }
        )
        
        logger.info(f"✅ Workflow completed for run: {run_id}")
        
        return GenerationResponse(
            success=True,
            run_id=run_id,
            message="Service generated successfully. Deployment pipeline triggered.",
            repository_url=workflow_result.get("repository_url"),
            deployment_status="pipeline_triggered",
            estimated_completion="5-10 minutes",
            artifacts=workflow_result.get("artifacts", {})
        )
        
    except Exception as e:
        logger.error(f"❌ Generation error: {e}")
        raise HTTPException(
            status_code=500, 
            detail=f"Generation failed: {str(e)}"
        )

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=int(os.getenv("PORT", 8080)))