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
    command: str
    context: Optional[Dict[str, Any]] = None


class AgentResponse(BaseModel):
    """Response model for agent commands"""
    success: bool
    message: str
    data: Optional[Dict[str, Any]] = None
    command: str


@router.post("/command", response_model=AgentResponse)
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
        agent = get_agent()
        response = agent.process_command(request.command)
        return AgentResponse(**response)
    except Exception as e:
        logger.error(f"Error processing command: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


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
