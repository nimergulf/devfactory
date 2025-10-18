"""
Run Manager - Persistence Layer
Manages workflow run data and persistence
"""
import logging
import uuid
from datetime import datetime
from typing import Dict, Any, List, Optional

logger = logging.getLogger(__name__)

class RunManager:
    """Manages workflow runs and their persistence"""
    
    def __init__(self):
        # In-memory storage for now
        # In production, this would use a database
        self.runs = {}
        
    async def create_run(
        self,
        service_name: str,
        request_data: Dict[str, Any]
    ) -> str:
        """Create a new workflow run"""
        run_id = str(uuid.uuid4())
        
        run_data = {
            "run_id": run_id,
            "service_name": service_name,
            "status": "created",
            "created_at": datetime.utcnow().isoformat(),
            "updated_at": datetime.utcnow().isoformat(),
            "request_data": request_data,
            "results": {},
            "artifacts": {},
            "stages": {}
        }
        
        self.runs[run_id] = run_data
        logger.info(f"📝 Created run: {run_id} for service: {service_name}")
        
        return run_id
    
    async def update_run_status(
        self,
        run_id: str,
        status: str,
        results: Optional[Dict[str, Any]] = None
    ):
        """Update run status and results"""
        if run_id not in self.runs:
            raise ValueError(f"Run not found: {run_id}")
        
        self.runs[run_id]["status"] = status
        self.runs[run_id]["updated_at"] = datetime.utcnow().isoformat()
        
        if results:
            self.runs[run_id]["results"].update(results)
        
        logger.info(f"📊 Updated run {run_id} status to: {status}")
    
    async def get_run_status(self, run_id: str) -> Dict[str, Any]:
        """Get run status and information"""
        if run_id not in self.runs:
            raise ValueError(f"Run not found: {run_id}")
        
        return self.runs[run_id]
    
    async def list_runs(
        self,
        limit: int = 10,
        offset: int = 0
    ) -> List[Dict[str, Any]]:
        """List recent runs"""
        runs_list = list(self.runs.values())
        runs_list.sort(key=lambda x: x["created_at"], reverse=True)
        
        return runs_list[offset:offset + limit]