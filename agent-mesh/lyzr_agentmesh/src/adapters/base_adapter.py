"""
Base adapter interface for AgentMesh.

Provides the interface for integrating agents with the mesh.
"""

from abc import ABC, abstractmethod
from typing import List, Dict, Any, Optional

from lyzr_agentmesh.src.core.mesh import AgentMesh


class BaseAgentAdapter(ABC):
    """
    Abstract base class for agent adapters.

    Adapters wrap agents and provide a standard interface for
    publishing insights to the mesh.
    """

    def __init__(
        self,
        agent_id: str,
        mesh: AgentMesh,
        framework: str,
        role: str
    ):
        """
        Initialize the adapter.

        Args:
            agent_id: Unique agent identifier
            mesh: AgentMesh instance
            framework: Framework name (langchain, crewai, openai, mock, custom)
            role: Agent role (sales, marketing, inventory, etc.)

        Note:
            Permissions are managed via roles in PostgreSQL, not passed here.
        """
        self.agent_id = agent_id
        self.mesh = mesh
        self.framework = framework
        self.role = role

        # Auto-register agent if not exists (checks PostgreSQL)
        if not mesh.pg_store.agent_exists(agent_id):
            mesh.register_agent(
                agent_id=agent_id,
                framework=framework,
                role=role
            )

    @abstractmethod
    def publish_insight(
        self,
        observation: str,
        tags: List[str],
        context: Optional[Dict[str, Any]] = None,
        insight_type: str = "observation",
        confidence: float = 1.0
    ) -> str:
        """
        Publish an insight to the mesh.

        Args:
            observation: The insight observation/content
            tags: List of tags/topics
            context: Additional context metadata
            insight_type: Type of insight (observation, pattern, decision, action)
            confidence: Confidence score (0-1)

        Returns:
            Insight ID

        Note:
            Permissions are derived from agent's role in PostgreSQL, not specified per insight.
        """
        pass

    def query_by_tags(
        self,
        tags: List[str],
        match_all: bool = False
    ) -> List[Dict[str, Any]]:
        """
        Query insights by tags (with agent's role for permission filtering).

        Args:
            tags: List of tags to search
            match_all: If True, must match ALL tags

        Returns:
            List of insights
        """
        return self.mesh.query_by_tags(tags, self.role, match_all)

    def query_by_agent(self, agent_id: str) -> List[Dict[str, Any]]:
        """
        Query insights by another agent.

        Args:
            agent_id: Agent ID to query

        Returns:
            List of insights (filtered by permissions)
        """
        return self.mesh.query_by_agent(agent_id, self.role)

    def add_relationship(
        self,
        source_id: str,
        target_id: str,
        relation_type: str,
        metadata: Optional[Dict[str, Any]] = None
    ) -> None:
        """
        Add a relationship between insights.

        Args:
            source_id: Source insight ID
            target_id: Target insight ID
            relation_type: Type of relationship (BUILDS_ON, LED_TO, etc.)
            metadata: Additional metadata
        """
        from lyzr_agentmesh.src.models.data_models import RelationType

        rel_type = RelationType[relation_type]
        self.mesh.add_relationship(source_id, target_id, rel_type, metadata)

    def get_my_insights(self) -> List[Dict[str, Any]]:
        """
        Get all insights published by this agent.

        Returns:
            List of insights
        """
        return self.mesh.query_by_agent(self.agent_id, self.role)

    def get_my_influence(self) -> Dict[str, Any]:
        """
        Get influence metrics for this agent.

        Returns:
            Dictionary with influence metrics
        """
        return self.mesh.get_agent_influence(self.agent_id)
