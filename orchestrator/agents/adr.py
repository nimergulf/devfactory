"""
Architecture Decision Record (ADR) Agent
Generates comprehensive architecture decision records for services
"""
import logging
from typing import Dict, Any, Optional
from orchestrator.agents.base import BaseAgent

logger = logging.getLogger(__name__)

class ADRAgent(BaseAgent):
    """Agent responsible for generating Architecture Decision Records"""
    
    def __init__(self):
        super().__init__("adr")
        
    async def execute(
        self, 
        service_name: str, 
        requirement: str, 
        context: Dict[str, Any],
        providers: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Generate an Architecture Decision Record
        
        Args:
            service_name: Name of the service
            requirement: Service requirements
            context: Additional context from previous agents
            providers: Available providers (llm, vcs, etc.)
            
        Returns:
            Dict containing the generated ADR
        """
        try:
            logger.info(f"📋 Generating ADR for service: {service_name}")
            
            llm_provider = providers.get("llm")
            if not llm_provider:
                raise ValueError("LLM provider not available")
            
            # Create ADR prompt
            adr_prompt = self._build_adr_prompt(service_name, requirement, context)
            
            # Generate ADR using LLM
            adr_content = await llm_provider.generate_content(
                prompt=adr_prompt,
                max_tokens=2000,
                temperature=0.3
            )
            
            # Fallback to template if LLM fails
            if not adr_content:
                adr_content = self._get_fallback_adr(service_name, requirement, context)
            
            logger.info(f"✅ ADR generated for service: {service_name}")
            
            return {
                "adr_content": adr_content,
                "filename": "ADR.md",
                "agent": self.name,
                "status": "completed"
            }
            
        except Exception as e:
            logger.error(f"❌ ADR generation failed: {e}")
            # Return fallback ADR
            return {
                "adr_content": self._get_fallback_adr(service_name, requirement, context),
                "filename": "ADR.md",
                "agent": self.name,
                "status": "completed_with_fallback",
                "error": str(e)
            }
    
    def _build_adr_prompt(self, service_name: str, requirement: str, context: Dict[str, Any]) -> str:
        """Build the ADR generation prompt"""
        architecture_type = context.get("architecture_type", "microservice")
        deployment_target = context.get("deployment_target", "cloud-run")
        
        return f"""You are an expert software architect creating an Architecture Decision Record (ADR).

Service Name: {service_name}
Requirements: {requirement}
Architecture Type: {architecture_type}
Deployment Target: {deployment_target}

Create a comprehensive ADR with the following sections:
1. Title: ADR: {service_name}
2. Status: Accepted
3. Context: Business and technical context for this service
4. Decision: Architectural decisions including:
   - Technology stack
   - Framework choice
   - Database selection
   - Security approach
   - Deployment strategy
   - Testing strategy
5. Consequences: Positive and negative outcomes of these decisions

Format as Markdown. Focus on enterprise-grade decisions and best practices.
"""
    
    def _get_fallback_adr(self, service_name: str, requirement: str, context: Dict[str, Any]) -> str:
        """Generate a fallback ADR template"""
        architecture_type = context.get("architecture_type", "microservice")
        deployment_target = context.get("deployment_target", "cloud-run")
        
        return f"""# ADR: {service_name}

## Status
Accepted

## Context
We need to build {service_name} as part of our {architecture_type} architecture.

**Requirements**: {requirement}

**Constraints**:
- Must be cloud-native and scalable
- Security-first approach
- Fast time-to-market
- Maintainable and testable

## Decision

### Technology Stack
- **Runtime**: Python 3.11+
- **Framework**: FastAPI
- **Database**: PostgreSQL (production) / In-memory (MVP)
- **Deployment**: {deployment_target}
- **Container**: Docker with distroless base
- **Testing**: pytest with coverage

### Architecture Decisions
- **API Design**: RESTful with OpenAPI specification
- **Security**: JWT authentication, input validation, HTTPS
- **Monitoring**: Structured logging, health checks, metrics
- **CI/CD**: Automated testing, security scanning, deployment

### Infrastructure
- **Cloud Provider**: Google Cloud Platform
- **Compute**: Cloud Run for serverless scaling
- **Storage**: Cloud SQL for PostgreSQL
- **Secrets**: Secret Manager
- **Monitoring**: Cloud Logging and Monitoring

## Consequences

### Positive
- Fast development with FastAPI
- Automatic scaling with Cloud Run
- Enterprise-grade security and monitoring
- Cost-effective serverless architecture
- Easy maintenance and updates

### Negative
- Vendor lock-in to GCP
- Cold start latency (minimal with Cloud Run)
- Python performance limitations for CPU-intensive tasks

### Risks & Mitigations
- **Risk**: API breaking changes
  - **Mitigation**: Versioning strategy and backward compatibility
- **Risk**: Database performance
  - **Mitigation**: Connection pooling and query optimization
- **Risk**: Security vulnerabilities
  - **Mitigation**: Regular security scans and dependency updates
"""