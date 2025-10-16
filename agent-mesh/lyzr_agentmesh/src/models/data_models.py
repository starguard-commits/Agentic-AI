"""
Data models for AgentMesh.

Defines the core data structures for agents, insights, and topics.
"""

from dataclasses import dataclass, field
from typing import List, Dict, Any, Optional
from datetime import datetime
from enum import Enum
import uuid


class RelationType(Enum):
    """
    Types of relationships between nodes in the mesh.

    Simplified to only essential relationships:
    - CREATED: Agent created Insight (automatic)
    - BUILDS_ON: Insight references another Insight
    - LED_TO: Insight caused another Insight
    """
    CREATED = "CREATED"
    BUILDS_ON = "BUILDS_ON"
    LED_TO = "LED_TO"


@dataclass
class Agent:
    """
    Represents an AI agent in the mesh.

    Note: This is a lightweight reference node in NetworkX.
    Full agent data and permissions are stored in PostgreSQL.
    """
    agent_id: str
    framework: str  # langchain, crewai, openai, custom
    role: str  # sales, marketing, inventory, etc.
    metadata: Dict[str, Any] = field(default_factory=dict)

    def __post_init__(self):
        """Validate agent data."""
        if not self.agent_id:
            raise ValueError("agent_id is required")
        if not self.role:
            raise ValueError("role is required")


@dataclass
class Insight:
    """
    Represents an insight/observation from an agent.

    Note: Permissions are NOT stored here - they are derived from the agent's role
    in PostgreSQL at query time. This ensures PostgreSQL is the single source of truth.
    """
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    agent_id: str = ""
    observation: str = ""
    timestamp: str = field(default_factory=lambda: datetime.utcnow().isoformat())
    tags: List[str] = field(default_factory=list)
    context: Dict[str, Any] = field(default_factory=dict)
    insight_type: str = "observation"  # observation, pattern, decision, action
    confidence: float = 1.0

    def __post_init__(self):
        """Validate insight data."""
        if not self.agent_id:
            raise ValueError("agent_id is required")
        if not self.observation:
            raise ValueError("observation is required")
        if not 0 <= self.confidence <= 1:
            raise ValueError("confidence must be between 0 and 1")


@dataclass
class Topic:
    """Represents a topic/tag in the mesh."""
    name: str
    popularity: int = 0  # number of insights about this topic
    metadata: Dict[str, Any] = field(default_factory=dict)

    def __post_init__(self):
        """Validate topic data."""
        if not self.name:
            raise ValueError("name is required")


@dataclass
class Relationship:
    """Represents a relationship between nodes."""
    source_id: str
    target_id: str
    relation_type: RelationType
    metadata: Dict[str, Any] = field(default_factory=dict)
    timestamp: str = field(default_factory=lambda: datetime.utcnow().isoformat())

    def __post_init__(self):
        """Validate relationship data."""
        if not self.source_id:
            raise ValueError("source_id is required")
        if not self.target_id:
            raise ValueError("target_id is required")
