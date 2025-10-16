"""
GraphQL resolvers for AgentMesh.

Contains resolver functions that connect GraphQL queries to the mesh.
"""

import graphene
from typing import Optional

from lyzr_agentmesh.src.api.schema import (
    Query
)
from lyzr_agentmesh.src.core.mesh import AgentMesh
from lyzr_agentmesh.src.models.data_models import RelationType


class AgentMeshQuery(Query):
    """
    Query class with resolvers that have access to the mesh instance.
    """

    def __init__(self, mesh: AgentMesh):
        """
        Initialize query with mesh instance.

        Args:
            mesh: AgentMesh instance
        """
        super().__init__()
        self.mesh = mesh

    def resolve_agents(self, info):
        """Get all agents."""
        agents = self.mesh.get_all_agents()
        return agents

    def resolve_agent(self, info, agent_id: str):
        """Get a specific agent by ID."""
        node = self.mesh.store.get_node(agent_id)
        if node and node.get('node_type') == 'agent':
            return {'id': agent_id, **node}
        return None

    def resolve_insights_by_tags(
        self,
        info,
        tags: list,
        role: Optional[str] = None,
        match_all: bool = False
    ):
        """Query insights by tags."""
        return self.mesh.query_by_tags(tags, role, match_all)

    def resolve_insights_by_agent(
        self,
        info,
        agent_id: str,
        role: Optional[str] = None
    ):
        """Query insights by agent."""
        return self.mesh.query_by_agent(agent_id, role)

    def resolve_insights_by_time(
        self,
        info,
        start_date: str,
        end_date: Optional[str] = None,
        role: Optional[str] = None
    ):
        """Query insights by time range."""
        return self.mesh.query_by_time(start_date, end_date, role)

    def resolve_insight_relationships(
        self,
        info,
        insight_id: str,
        relation_type: Optional[str] = None,
        direction: str = "both"
    ):
        """Get relationships for an insight."""
        # Convert string to RelationType enum if provided
        rel_type_enum = None
        if relation_type:
            try:
                rel_type_enum = RelationType[relation_type]
            except KeyError:
                return []

        return self.mesh.get_insight_relationships(
            insight_id,
            rel_type_enum,
            direction
        )

    def resolve_agent_influence(self, info, agent_id: str):
        """Get influence metrics for an agent."""
        return self.mesh.get_agent_influence(agent_id)

    def resolve_topics(self, info):
        """Get all topics."""
        return self.mesh.get_all_topics()

    def resolve_mesh_stats(self, info):
        """Get mesh statistics."""
        return self.mesh.get_stats()


def create_schema(mesh: AgentMesh) -> graphene.Schema:
    """
    Create a GraphQL schema with resolvers bound to a mesh instance.

    Args:
        mesh: AgentMesh instance

    Returns:
        Graphene schema
    """
    # Create a query class with mesh instance
    class QueryWithMesh(Query):
        """Query class with mesh-specific resolvers."""
        pass

    # Bind resolvers
    def resolve_agents(root, info):
        agents = mesh.get_all_agents()
        return agents

    def resolve_agent(root, info, agent_id: str):
        node = mesh.store.get_node(agent_id)
        if node and node.get('node_type') == 'agent':
            return {'id': agent_id, **node}
        return None

    def resolve_insights_by_tags(
        root,
        info,
        tags: list,
        role: Optional[str] = None,
        match_all: bool = False
    ):
        return mesh.query_by_tags(tags, role, match_all)

    def resolve_insights_by_agent(
        root,
        info,
        agent_id: str,
        role: Optional[str] = None
    ):
        return mesh.query_by_agent(agent_id, role)

    def resolve_insights_by_time(
        root,
        info,
        start_date: str,
        end_date: Optional[str] = None,
        role: Optional[str] = None
    ):
        return mesh.query_by_time(start_date, end_date, role)

    def resolve_insight_relationships(
        root,
        info,
        insight_id: str,
        relation_type: Optional[str] = None,
        direction: str = "both"
    ):
        rel_type_enum = None
        if relation_type:
            try:
                rel_type_enum = RelationType[relation_type]
            except KeyError:
                return []

        return mesh.get_insight_relationships(
            insight_id,
            rel_type_enum,
            direction
        )

    def resolve_agent_influence(root, info, agent_id: str):
        return mesh.get_agent_influence(agent_id)

    def resolve_topics(root, info):
        return mesh.get_all_topics()

    def resolve_mesh_stats(root, info):
        return mesh.get_stats()

    # Attach resolvers to Query class
    QueryWithMesh.resolve_agents = resolve_agents
    QueryWithMesh.resolve_agent = resolve_agent
    QueryWithMesh.resolve_insights_by_tags = resolve_insights_by_tags
    QueryWithMesh.resolve_insights_by_agent = resolve_insights_by_agent
    QueryWithMesh.resolve_insights_by_time = resolve_insights_by_time
    QueryWithMesh.resolve_insight_relationships = resolve_insight_relationships
    QueryWithMesh.resolve_agent_influence = resolve_agent_influence
    QueryWithMesh.resolve_topics = resolve_topics
    QueryWithMesh.resolve_mesh_stats = resolve_mesh_stats

    return graphene.Schema(query=QueryWithMesh)


def execute_query(schema: graphene.Schema, query_string: str):
    """
    Execute a GraphQL query.

    Args:
        schema: Graphene schema
        query_string: GraphQL query string

    Returns:
        Query result
    """
    result = schema.execute(query_string)

    if result.errors:
        return {
            'errors': [str(e) for e in result.errors],
            'data': None
        }

    return {
        'errors': None,
        'data': result.data
    }
