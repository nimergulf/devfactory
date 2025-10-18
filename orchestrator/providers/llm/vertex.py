"""
Vertex AI LLM Provider
Google Vertex AI integration with Gemini models
"""
import os
import logging
from typing import Dict, Any, Optional, List
import google.genai as genai

logger = logging.getLogger(__name__)

class VertexAIProvider:
    """Vertex AI LLM provider with Gemini models"""
    
    def __init__(self, project_id: str, region: str = "us-central1"):
        self.project_id = project_id
        self.region = region
        self.client = None
        self._setup_client()
        
        # Model preferences (in order of preference)
        self.preferred_models = [
            os.getenv("GENAI_MODEL", "gemini-2.5-flash"),
            "gemini-2.0-flash", 
            "gemini-1.5-pro",
            "gemini-1.5-flash",
        ]
        
    def _setup_client(self):
        """Initialize the Google Gen AI client"""
        try:
            # Set up for Vertex AI mode with ADC
            os.environ["GOOGLE_CLOUD_PROJECT"] = self.project_id
            os.environ["GOOGLE_CLOUD_LOCATION"] = self.region
            os.environ["GOOGLE_GENAI_USE_VERTEXAI"] = "true"
            
            # Initialize client
            self.client = genai.Client()
            logger.info(f"✅ Vertex AI client initialized for project: {self.project_id}")
            
        except Exception as e:
            logger.error(f"❌ Failed to initialize Vertex AI client: {e}")
            self.client = None
    
    async def generate_content(
        self,
        prompt: str,
        max_tokens: int = 1000,
        temperature: float = 0.7,
        model: Optional[str] = None
    ) -> Optional[str]:
        """
        Generate content using Vertex AI Gemini models
        
        Args:
            prompt: The input prompt
            max_tokens: Maximum tokens to generate
            temperature: Sampling temperature (0.0 to 1.0)
            model: Specific model to use (optional)
            
        Returns:
            Generated content or None if all models fail
        """
        if not self.client:
            logger.error("❌ Vertex AI client not initialized")
            return None
            
        models_to_try = [model] if model else self.preferred_models
        
        for model_name in models_to_try:
            try:
                logger.info(f"🔍 Trying model: {model_name}")
                
                response = self.client.models.generate_content(
                    model=model_name,
                    contents=[{
                        "role": "user",
                        "parts": [{"text": prompt}]
                    }],
                    generation_config={
                        "max_output_tokens": max_tokens,
                        "temperature": temperature,
                        "top_p": 0.9,
                        "top_k": 40
                    }
                )
                
                if response.candidates and len(response.candidates) > 0:
                    content = response.candidates[0].content.parts[0].text
                    logger.info(f"✅ SUCCESS with model: {model_name}")
                    return content
                
            except Exception as e:
                logger.warning(f"❌ Model {model_name} failed: {e}")
                continue
        
        logger.warning("⚠️ All AI models failed")
        return None
    
    async def health_check(self) -> Dict[str, Any]:
        """Health check for the Vertex AI provider"""
        try:
            if not self.client:
                return {
                    "provider": "vertex-ai",
                    "status": "unhealthy",
                    "error": "Client not initialized"
                }
            
            # Try a simple generation to test connectivity
            test_prompt = "Hello, this is a test."
            result = await self.generate_content(test_prompt, max_tokens=10)
            
            return {
                "provider": "vertex-ai",
                "status": "healthy" if result else "degraded",
                "project_id": self.project_id,
                "region": self.region,
                "available_models": len(self.preferred_models),
                "test_generation": bool(result)
            }
            
        except Exception as e:
            return {
                "provider": "vertex-ai",
                "status": "unhealthy",
                "error": str(e)
            }
    
    async def list_available_models(self) -> List[str]:
        """List available models"""
        try:
            if not self.client:
                return []
            
            # For now, return the preferred models
            # In a full implementation, this would query the API for available models
            return self.preferred_models
            
        except Exception as e:
            logger.error(f"❌ Failed to list models: {e}")
            return []
    
    async def get_model_info(self, model_name: str) -> Dict[str, Any]:
        """Get information about a specific model"""
        try:
            return {
                "model_name": model_name,
                "provider": "vertex-ai",
                "available": model_name in self.preferred_models,
                "max_tokens": 8192 if "gemini-2" in model_name else 4096,
                "supports_system_prompt": True,
                "supports_function_calling": True
            }
            
        except Exception as e:
            logger.error(f"❌ Failed to get model info: {e}")
            return {"model_name": model_name, "available": False, "error": str(e)}