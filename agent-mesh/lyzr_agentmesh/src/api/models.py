"""
Pydantic models for FastAPI request/response validation.
"""

from typing import List, Dict, Any, Optional
from pydantic import BaseModel, Field


class AgentRegistration(BaseModel):
    """Request to register a new agent."""
    agent_id: str = Field(..., description="Unique agent identifier")
    framework: str = Field(..., description="Framework name (langchain, crewai, openai, custom)")
    role: str = Field(..., description="Agent role (sales, marketing, inventory, etc.)")
    metadata: Optional[Dict[str, Any]] = Field(default=None, description="Additional metadata")


class PublishInsightRequest(BaseModel):
    """Request to publish an insight."""
    agent_id: str = Field(..., description="ID of agent publishing the insight")
    observation: str = Field(..., description="The insight observation/content")
    tags: List[str] = Field(..., description="List of tags/topics")
    context: Optional[Dict[str, Any]] = Field(default=None, description="Additional context")
    insight_type: str = Field(default="observation", description="Type: observation, pattern, decision, action")
    confidence: float = Field(default=1.0, ge=0.0, le=1.0, description="Confidence score 0-1")


class AddRelationshipRequest(BaseModel):
    """Request to add a relationship between insights."""
    source_id: str = Field(..., description="Source insight ID")
    target_id: str = Field(..., description="Target insight ID")
    relation_type: str = Field(..., description="Relationship type: BUILDS_ON, LED_TO")
    metadata: Optional[Dict[str, Any]] = Field(default=None, description="Additional metadata")


class QueryByTagsRequest(BaseModel):
    """Request to query insights by tags."""
    tags: List[str] = Field(..., description="List of tags to search")
    requester_role: str = Field(..., description="Role of requester for permission filtering")
    match_all: bool = Field(default=False, description="If true, match ALL tags. If false, match ANY")


class InsightResponse(BaseModel):
    """Response containing insight data."""
    id: str
    agent_id: str
    observation: str
    timestamp: str
    tags: List[str]
    context: Dict[str, Any]
    insight_type: str
    confidence: float


class AgentResponse(BaseModel):
    """Response containing agent data."""
    agent_id: str
    framework: str
    role: str
    metadata: Dict[str, Any]


class PublishInsightResponse(BaseModel):
    """Response after publishing an insight."""
    insight_id: str
    message: str = "Insight published successfully"


class AddRelationshipResponse(BaseModel):
    """Response after adding a relationship."""
    message: str = "Relationship created successfully"


class HealthResponse(BaseModel):
    """Health check response."""
    status: str
    postgres_connected: bool
    graph_nodes: int
    graph_edges: int


class ErrorResponse(BaseModel):
    """Error response."""
    error: str
    detail: Optional[str] = None
