"""
Base Agent Class
Abstract base class for all DevFactory agents
"""
import logging
from abc import ABC, abstractmethod
from typing import Dict, Any, Optional
import uuid
from datetime import datetime

logger = logging.getLogger(__name__)

class BaseAgent(ABC):
    """Abstract base class for all DevFactory agents"""
    
    def __init__(self, name: str):
        self.name = name
        self.agent_id = str(uuid.uuid4())
        self.created_at = datetime.utcnow()
        
    @abstractmethod
    async def execute(
        self, 
        service_name: str, 
        requirement: str, 
        context: Dict[str, Any],
        providers: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Execute the agent's main functionality
        
        Args:
            service_name: Name of the service being generated
            requirement: Service requirements
            context: Context from previous agents and workflow
            providers: Available providers (llm, vcs, ci, etc.)
            
        Returns:
            Dict containing the agent's output
        """
        pass
    
    def get_metadata(self) -> Dict[str, Any]:
        """Get agent metadata"""
        return {
            "agent_name": self.name,
            "agent_id": self.agent_id,
            "created_at": self.created_at.isoformat(),
        }
    
    async def health_check(self) -> Dict[str, Any]:
        """Health check for the agent"""
        return {
            "agent": self.name,
            "status": "healthy",
            "timestamp": datetime.utcnow().isoformat()
        }
    
    def _log_execution_start(self, service_name: str):
        """Log execution start"""
        logger.info(f"🚀 {self.name.upper()} Agent starting execution for: {service_name}")
    
    def _log_execution_complete(self, service_name: str):
        """Log execution completion"""
        logger.info(f"✅ {self.name.upper()} Agent completed execution for: {service_name}")
    
    def _log_execution_error(self, service_name: str, error: Exception):
        """Log execution error"""
        logger.error(f"❌ {self.name.upper()} Agent failed for {service_name}: {error}")

class AgentRegistry:
    """Registry for managing agents"""
    
    def __init__(self):
        self._agents = {}
    
    def register(self, agent: BaseAgent):
        """Register an agent"""
        self._agents[agent.name] = agent
        logger.info(f"📝 Registered agent: {agent.name}")
    
    def get(self, name: str) -> Optional[BaseAgent]:
        """Get an agent by name"""
        return self._agents.get(name)
    
    def list_agents(self) -> Dict[str, BaseAgent]:
        """List all registered agents"""
        return self._agents.copy()
    
    async def health_check_all(self) -> Dict[str, Dict[str, Any]]:
        """Health check all agents"""
        results = {}
        for name, agent in self._agents.items():
            try:
                results[name] = await agent.health_check()
            except Exception as e:
                results[name] = {
                    "agent": name,
                    "status": "unhealthy",
                    "error": str(e),
                    "timestamp": datetime.utcnow().isoformat()
                }
        return results