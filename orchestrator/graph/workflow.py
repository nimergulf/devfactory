"""
Workflow Orchestrator
Manages the execution flow of agents in the DevFactory platform
"""
import logging
from typing import Dict, Any, List, Optional
import asyncio
from datetime import datetime
import uuid

from orchestrator.agents.base import AgentRegistry
from orchestrator.agents.adr import ADRAgent
from orchestrator.agents.api import APIAgent

logger = logging.getLogger(__name__)

class WorkflowOrchestrator:
    """Orchestrates the execution of multiple agents in a workflow"""
    
    def __init__(self):
        self.agent_registry = AgentRegistry()
        self._setup_agents()
        
    def _setup_agents(self):
        """Initialize and register all agents"""
        # Register core agents
        self.agent_registry.register(ADRAgent())
        self.agent_registry.register(APIAgent())
        
        logger.info("🔧 Workflow orchestrator initialized with agents")
        
    async def execute_generation_workflow(
        self,
        run_id: str,
        service_name: str,
        requirement: str,
        architecture_type: str = "microservice",
        deployment_target: str = "cloud-run",
        security_level: str = "standard",
        metadata: Optional[Dict[str, Any]] = None,
        providers: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Execute the complete service generation workflow
        
        Args:
            run_id: Unique identifier for this workflow run
            service_name: Name of the service to generate
            requirement: Service requirements
            architecture_type: Type of architecture (microservice, monolith, etc.)
            deployment_target: Target deployment platform
            security_level: Security requirements level
            metadata: Additional metadata
            providers: Available providers (llm, vcs, ci, etc.)
            
        Returns:
            Dict containing workflow results
        """
        workflow_start = datetime.utcnow()
        logger.info(f"🎬 Starting workflow for run: {run_id}")
        
        # Initialize context
        context = {
            "run_id": run_id,
            "service_name": service_name,
            "requirement": requirement,
            "architecture_type": architecture_type,
            "deployment_target": deployment_target,
            "security_level": security_level,
            "metadata": metadata or {},
            "workflow_start": workflow_start,
            "artifacts": {}
        }
        
        providers = providers or {}
        results = {}
        
        try:
            # Define workflow stages
            workflow_stages = [
                {
                    "name": "research",
                    "agents": ["research"],
                    "parallel": False
                },
                {
                    "name": "architecture",
                    "agents": ["adr"],
                    "parallel": False
                },
                {
                    "name": "design",
                    "agents": ["api"],
                    "parallel": False
                },
                {
                    "name": "implementation",
                    "agents": ["code"],
                    "parallel": False
                },
                {
                    "name": "testing",
                    "agents": ["test"],
                    "parallel": False
                },
                {
                    "name": "infrastructure",
                    "agents": ["iac"],
                    "parallel": False
                }
            ]
            
            # Execute workflow stages
            for stage in workflow_stages:
                stage_name = stage["name"]
                agents = stage["agents"]
                parallel = stage.get("parallel", False)
                
                logger.info(f"🚀 Executing stage: {stage_name}")
                
                if parallel:
                    # Execute agents in parallel
                    stage_results = await self._execute_agents_parallel(
                        agents, service_name, requirement, context, providers
                    )
                else:
                    # Execute agents sequentially
                    stage_results = await self._execute_agents_sequential(
                        agents, service_name, requirement, context, providers
                    )
                
                # Update context with stage results
                results[stage_name] = stage_results
                context["artifacts"].update(stage_results)
                
                logger.info(f"✅ Stage {stage_name} completed")
            
            # Finalize workflow
            await self._finalize_workflow(context, results, providers)
            
            workflow_end = datetime.utcnow()
            duration = (workflow_end - workflow_start).total_seconds()
            
            logger.info(f"🎉 Workflow completed for run: {run_id} in {duration:.2f}s")
            
            return {
                "run_id": run_id,
                "status": "completed",
                "duration_seconds": duration,
                "artifacts": context["artifacts"],
                "repository_url": results.get("repository_url"),
                "stages": results
            }
            
        except Exception as e:
            logger.error(f"❌ Workflow failed for run: {run_id}: {e}")
            return {
                "run_id": run_id,
                "status": "failed",
                "error": str(e),
                "artifacts": context.get("artifacts", {}),
                "stages": results
            }
    
    async def _execute_agents_sequential(
        self,
        agent_names: List[str],
        service_name: str,
        requirement: str,
        context: Dict[str, Any],
        providers: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Execute agents sequentially"""
        results = {}
        
        for agent_name in agent_names:
            agent = self.agent_registry.get(agent_name)
            if not agent:
                logger.warning(f"⚠️ Agent not found: {agent_name}")
                continue
                
            try:
                agent_result = await agent.execute(
                    service_name=service_name,
                    requirement=requirement,
                    context=context,
                    providers=providers
                )
                results[agent_name] = agent_result
                
                # Update context for next agent
                context.update(agent_result)
                
            except Exception as e:
                logger.error(f"❌ Agent {agent_name} failed: {e}")
                results[agent_name] = {
                    "status": "failed",
                    "error": str(e),
                    "agent": agent_name
                }
        
        return results
    
    async def _execute_agents_parallel(
        self,
        agent_names: List[str],
        service_name: str,
        requirement: str,
        context: Dict[str, Any],
        providers: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Execute agents in parallel"""
        tasks = []
        
        for agent_name in agent_names:
            agent = self.agent_registry.get(agent_name)
            if not agent:
                logger.warning(f"⚠️ Agent not found: {agent_name}")
                continue
                
            task = asyncio.create_task(
                agent.execute(
                    service_name=service_name,
                    requirement=requirement,
                    context=context.copy(),  # Each agent gets its own context copy
                    providers=providers
                ),
                name=agent_name
            )
            tasks.append(task)
        
        # Wait for all tasks to complete
        task_results = await asyncio.gather(*tasks, return_exceptions=True)
        
        # Process results
        results = {}
        for i, result in enumerate(task_results):
            agent_name = agent_names[i]
            if isinstance(result, Exception):
                results[agent_name] = {
                    "status": "failed",
                    "error": str(result),
                    "agent": agent_name
                }
            else:
                results[agent_name] = result
        
        return results
    
    async def _finalize_workflow(
        self,
        context: Dict[str, Any],
        results: Dict[str, Any],
        providers: Dict[str, Any]
    ):
        """Finalize the workflow by committing to VCS and triggering CI"""
        logger.info("🔄 Finalizing workflow...")
        
        try:
            # Get VCS and CI providers
            vcs_provider = providers.get("vcs")
            ci_provider = providers.get("ci")
            
            if vcs_provider:
                # Commit artifacts to repository
                commit_result = await vcs_provider.commit_artifacts(
                    service_name=context["service_name"],
                    artifacts=context["artifacts"],
                    commit_message=f"[DevFactory] Generate service: {context['service_name']}"
                )
                results["repository_url"] = commit_result.get("repository_url")
                logger.info("✅ Artifacts committed to repository")
                
            if ci_provider:
                # Trigger CI/CD pipeline
                pipeline_result = await ci_provider.trigger_pipeline(
                    service_name=context["service_name"],
                    repository_url=results.get("repository_url")
                )
                results["pipeline_id"] = pipeline_result.get("pipeline_id")
                logger.info("✅ CI/CD pipeline triggered")
                
        except Exception as e:
            logger.error(f"❌ Workflow finalization failed: {e}")
            results["finalization_error"] = str(e)
    
    async def get_workflow_status(self, run_id: str) -> Dict[str, Any]:
        """Get the status of a workflow run"""
        # This would typically query a database or cache
        # For now, return a placeholder
        return {
            "run_id": run_id,
            "status": "unknown",
            "message": "Status tracking not implemented yet"
        }
    
    async def health_check(self) -> Dict[str, Any]:
        """Health check for the workflow orchestrator"""
        agent_health = await self.agent_registry.health_check_all()
        
        return {
            "orchestrator": "healthy",
            "timestamp": datetime.utcnow().isoformat(),
            "agents": agent_health
        }