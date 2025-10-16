"""
GraphQL schema definitions for AgentMesh.

Defines the types and queries available via the GraphQL API.
"""

import graphene
from typing import List, Optional


class Agent(graphene.ObjectType):
    """
    Agent type in the mesh.

    Note: Permissions are NOT exposed here - they are managed in PostgreSQL
    and derived at query time based on agent's role.
    """
    id = graphene.String(required=True)
    framework = graphene.String()
    role = graphene.String()
    # permissions removed - managed in PostgreSQL
    metadata = graphene.JSONString()


class Topic(graphene.ObjectType):
    """Topic/tag type in the mesh."""
    id = graphene.String(required=True)
    name = graphene.String()
    popularity = graphene.Int()
    metadata = graphene.JSONString()


class Insight(graphene.ObjectType):
    """
    Insight type in the mesh.

    Note: Permissions are NOT stored in insights - they are derived from
    the creator agent's role in PostgreSQL at query time.
    """
    id = graphene.String(required=True)
    agent_id = graphene.String()
    observation = graphene.String()
    timestamp = graphene.String()
    tags = graphene.List(graphene.String)
    # permissions removed - derived from agent's role in PostgreSQL
    context = graphene.JSONString()
    insight_type = graphene.String()
    confidence = graphene.Float()


class Relationship(graphene.ObjectType):
    """Relationship between nodes."""
    source = graphene.String(required=True)
    target = graphene.String(required=True)
    relation_type = graphene.String()
    metadata = graphene.JSONString()
    timestamp = graphene.String()


class AgentInfluence(graphene.ObjectType):
    """Influence metrics for an agent."""
    agent_id = graphene.String(required=True)
    insights_published = graphene.Int()
    accessed_by_agents = graphene.List(graphene.String)
    influenced_count = graphene.Int()
    builds_on_count = graphene.Int()
    led_to_count = graphene.Int()


class MeshStats(graphene.ObjectType):
    """Statistics about the mesh."""
    total_nodes = graphene.Int()
    total_edges = graphene.Int()
    agents = graphene.Int()
    insights = graphene.Int()
    topics = graphene.Int()
    unique_tags = graphene.Int()


class Query(graphene.ObjectType):
    """Root query type."""

    # Agent queries
    agents = graphene.List(
        Agent,
        description="Get all agents in the mesh"
    )

    agent = graphene.Field(
        Agent,
        agent_id=graphene.String(required=True),
        description="Get a specific agent by ID"
    )

    # Insight queries
    insights_by_tags = graphene.List(
        Insight,
        tags=graphene.List(graphene.String, required=True),
        role=graphene.String(),
        match_all=graphene.Boolean(default_value=False),
        description="Query insights by tags with optional permission filtering"
    )

    insights_by_agent = graphene.List(
        Insight,
        agent_id=graphene.String(required=True),
        role=graphene.String(),
        description="Query insights created by a specific agent"
    )

    insights_by_time = graphene.List(
        Insight,
        start_date=graphene.String(required=True),
        end_date=graphene.String(),
        role=graphene.String(),
        description="Query insights by time range (YYYY-MM-DD format)"
    )

    # Relationship queries
    insight_relationships = graphene.List(
        Relationship,
        insight_id=graphene.String(required=True),
        relation_type=graphene.String(),
        direction=graphene.String(default_value="both"),
        description="Get relationships for an insight"
    )

    # Influence queries
    agent_influence = graphene.Field(
        AgentInfluence,
        agent_id=graphene.String(required=True),
        description="Get influence metrics for an agent"
    )

    # Topic queries
    topics = graphene.List(
        Topic,
        description="Get all topics in the mesh"
    )

    # Stats
    mesh_stats = graphene.Field(
        MeshStats,
        description="Get mesh statistics"
    )


# Schema will be created in resolvers.py after mesh instance is available
