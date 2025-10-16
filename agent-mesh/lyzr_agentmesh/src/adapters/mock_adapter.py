"""
Mock agent adapter for AgentMesh.

Simple adapter implementation for mock/test agents.
"""

from typing import List, Dict, Any, Optional

from lyzr_agentmesh.src.adapters.base_adapter import BaseAgentAdapter


class AgentMeshAdapter(BaseAgentAdapter):
    """
    Standard adapter for mock agents.

    This is the main adapter that mock agents will use to interact with the mesh.
    """

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

        Automatically includes framework and role context.

        Args:
            observation: The insight observation/content
            tags: List of tags/topics
            context: Additional context metadata
            insight_type: Type of insight (observation, pattern, decision, action)
            confidence: Confidence score (0-1)

        Returns:
            Insight ID

        Note:
            Permissions are derived from agent's role in PostgreSQL.
        """
        # Merge context with framework/role metadata
        full_context = {
            'framework': self.framework,
            'agent_role': self.role,
            **(context or {})
        }

        return self.mesh.publish_insight(
            agent_id=self.agent_id,
            observation=observation,
            tags=tags,
            context=full_context,
            insight_type=insight_type,
            confidence=confidence
        )


class LangChainAdapter(BaseAgentAdapter):
    """
    Adapter for LangChain agents.

    Can be extended to intercept LangChain agent callbacks.
    """

    def publish_insight(
        self,
        observation: str,
        tags: List[str],
        context: Optional[Dict[str, Any]] = None,
        insight_type: str = "observation",
        confidence: float = 1.0
    ) -> str:
        """Publish insight with LangChain-specific context."""
        full_context = {
            'framework': 'langchain',
            'agent_role': self.role,
            'framework_version': 'langchain>=0.1.0',
            **(context or {})
        }

        return self.mesh.publish_insight(
            agent_id=self.agent_id,
            observation=observation,
            tags=tags,
            context=full_context,
            insight_type=insight_type,
            confidence=confidence
        )


class OpenAIAdapter(BaseAgentAdapter):
    """
    Adapter for OpenAI SDK agents.

    Can be extended to work with OpenAI Assistants API.
    """

    def publish_insight(
        self,
        observation: str,
        tags: List[str],
        context: Optional[Dict[str, Any]] = None,
        insight_type: str = "observation",
        confidence: float = 1.0
    ) -> str:
        """Publish insight with OpenAI-specific context."""
        full_context = {
            'framework': 'openai',
            'agent_role': self.role,
            'framework_version': 'openai>=1.0.0',
            **(context or {})
        }

        return self.mesh.publish_insight(
            agent_id=self.agent_id,
            observation=observation,
            tags=tags,
            context=full_context,
            insight_type=insight_type,
            confidence=confidence
        )
