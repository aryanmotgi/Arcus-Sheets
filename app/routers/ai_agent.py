"""
FastAPI router for AI Agent endpoints
"""
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Optional, Dict, Any
import logging
import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent / "src"))

from ai_agent import SheetsAIAgent

logger = logging.getLogger(__name__)

router = APIRouter()

# Initialize agent (singleton)
_agent: Optional[SheetsAIAgent] = None


def get_agent() -> SheetsAIAgent:
    """Get or create the AI agent instance"""
    global _agent
    if _agent is None:
        try:
            _agent = SheetsAIAgent()
        except Exception as e:
            logger.error(f"Failed to initialize AI agent: {e}")
            raise HTTPException(status_code=500, detail=f"Failed to initialize agent: {str(e)}")
    return _agent


class AgentCommand(BaseModel):
    """Request model for agent commands"""
    command: Optional[str] = None
    text: Optional[str] = None
    message: Optional[str] = None
    prompt: Optional[str] = None
    context: Optional[Dict[str, Any]] = None
    
    def get_command(self) -> str:
        """Get command from any of the possible fields"""
        return (
            self.command or 
            self.text or 
            self.message or 
            self.prompt or 
            ""
        ).strip()


class AgentResponse(BaseModel):
    """Response model for agent commands"""
    success: bool
    message: str
    data: Optional[Dict[str, Any]] = None
    command: str


@router.post("/command")
async def process_command(request: AgentCommand):
    """
    Process a natural language command with the AI agent
    
    Examples:
    - "sync orders from shopify"
    - "show me total revenue"
    - "update the orders sheet"
    - "what's my profit breakdown?"
    - "backup PSL values"
    """
    try:
        # Get command from any field
        command = request.get_command()
        
        # Log request
        logger.info(f"=== API Request ===")
        logger.info(f"Command received: '{command}'")
        logger.info(f"Full request: {request.dict()}")
        
        if not command:
            logger.warning("Empty command received")
            return {
                "success": False,
                "message": "No command provided. Please send a command in the 'command' field.",
                "data": None,
                "command": ""
            }
        
        # Process command
        agent = get_agent()
        response = agent.process_command(command)
        
        # Ensure response has required fields
        if not isinstance(response, dict):
            response = {"success": False, "message": "Invalid response format", "data": None}
        
        # Add command to response if missing
        if "command" not in response:
            response["command"] = command
        
        # Log response
        logger.info(f"=== API Response ===")
        logger.info(f"Success: {response.get('success', False)}")
        logger.info(f"Message: {response.get('message', '')[:100]}...")
        
        return response
    except Exception as e:
        logger.error(f"Error processing command: {e}", exc_info=True)
        return {
            "success": False,
            "message": f"Error processing command: {str(e)}",
            "data": None,
            "command": request.get_command() if hasattr(request, 'get_command') else ""
        }


@router.get("/capabilities")
async def get_capabilities():
    """Get list of available commands and capabilities"""
    return {
        "available_commands": [
            {
                "command": "sync orders",
                "description": "Sync orders from Shopify to Google Sheets",
                "example": "sync orders from shopify"
            },
            {
                "command": "show revenue",
                "description": "Get total revenue and sales information",
                "example": "show me total revenue"
            },
            {
                "command": "orders summary",
                "description": "Get summary of orders from Shopify",
                "example": "give me orders summary"
            },
            {
                "command": "product sales",
                "description": "Get breakdown of product sales",
                "example": "what products have sold the most?"
            },
            {
                "command": "profit breakdown",
                "description": "Get profit analysis and breakdown",
                "example": "show me profit breakdown"
            },
            {
                "command": "backup PSL",
                "description": "Backup PSL (Private Shipping Label) values",
                "example": "backup PSL values"
            },
            {
                "command": "restore PSL",
                "description": "Restore PSL values from backup",
                "example": "restore PSL values"
            },
            {
                "command": "customer insights",
                "description": "Get customer purchase insights",
                "example": "show me customer insights"
            }
        ]
    }


@router.get("/health")
async def agent_health():
    """Check if the AI agent is healthy and ready"""
    try:
        agent = get_agent()
        return {
            "status": "healthy",
            "agent_initialized": True,
            "capabilities": len(agent.available_commands)
        }
    except Exception as e:
        return {
            "status": "unhealthy",
            "agent_initialized": False,
            "error": str(e)
        }
