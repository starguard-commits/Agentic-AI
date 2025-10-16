"""
AgentMesh - Main interface for the knowledge mesh.

Provides high-level operations for publishing insights, querying,
and managing relationships between agents and insights.
"""

from typing import List, Dict, Any, Optional

from lyzr_agentmesh.src.core.graph_store import GraphStore
from lyzr_agentmesh.src.core.pg_store import PostgreSQLStore
from lyzr_agentmesh.src.core.permissions import PermissionManager
from lyzr_agentmesh.src.models.data_models import Agent, Insight, Topic, Relationship, RelationType


class AgentMesh:
    """
    Main AgentMesh class that provides the interface for multi-agent knowledge sharing.

    Uses hybrid storage:
    - PostgreSQL: Agents, roles, permissions, audit logs
    - NetworkX: Insights, topics, relationships (graph data)
    """

    def __init__(
        self,
        persist_path: Optional[str] = "agentmesh.pkl",
        pg_config: Optional[Dict[str, Any]] = None
    ):
        """
        Initialize AgentMesh.

        Args:
            persist_path: Path to persist the graph (None to disable persistence)
            pg_config: PostgreSQL connection config (host, port, database, user, password)
        """
        # NetworkX for insights and relationships (knowledge graph)
        self.store = GraphStore(persist_path)

        # PostgreSQL for agents, roles, and audit logs (mandatory)
        pg_config = pg_config or {}
        self.pg_store = PostgreSQLStore(**pg_config)

        # Legacy permission manager (kept for backward compatibility)
        self.permission_manager = PermissionManager()

    def register_agent(
        self,
        agent_id: str,
        framework: str,
        role: str,
        metadata: Optional[Dict[str, Any]] = None
    ) -> str:
        """
        Register a new agent in the mesh.

        Args:
            agent_id: Unique agent identifier
            framework: Framework used (langchain, crewai, openai, custom)
            role: Agent role (sales, marketing, inventory, etc.)
            metadata: Additional metadata

        Returns:
            Agent ID

        Note:
            Permissions are managed via roles in PostgreSQL, not stored in graph.
        """
        # Register in PostgreSQL (source of truth for agents and permissions)
        self.pg_store.register_agent(agent_id, framework, role, metadata)

        # Create lightweight reference in NetworkX (for graph operations)
        agent = Agent(
            agent_id=agent_id,
            framework=framework,
            role=role,
            metadata=metadata or {}
        )
        self.store.add_agent_node(agent)

        return agent_id

    def publish_insight(
        self,
        agent_id: str,
        observation: str,
        tags: List[str],
        context: Optional[Dict[str, Any]] = None,
        insight_type: str = "observation",
        confidence: float = 1.0
    ) -> str:
        """
        Publish an insight to the mesh.

        Args:
            agent_id: ID of agent publishing the insight
            observation: The insight observation/content
            tags: List of tags/topics
            context: Additional context metadata
            insight_type: Type of insight (observation, pattern, decision, action)
            confidence: Confidence score (0-1)

        Returns:
            Insight ID

        Raises:
            ValueError: If agent is not registered

        Note:
            Permissions are NOT stored in the insight. They are derived from the agent's
            role in PostgreSQL at query time.
        """
        # Validate agent exists in PostgreSQL
        if not self.pg_store.agent_exists(agent_id):
            raise ValueError(f"Agent '{agent_id}' is not registered. Please register the agent first.")

        insight = Insight(
            agent_id=agent_id,
            observation=observation,
            tags=tags,
            context=context or {},
            insight_type=insight_type,
            confidence=confidence
        )

        insight_id = self.store.add_insight_node(insight)

        # Create CREATED relationship
        created_rel = Relationship(
            source_id=agent_id,
            target_id=insight_id,
            relation_type=RelationType.CREATED
        )
        self.store.add_relationship(created_rel)

        # Track topics for popularity (no ABOUT relationships - tags stored in insight)
        for tag in tags:
            self._ensure_topic(tag)

        # Audit log the insight publication
        self.pg_store.log_action(
            agent_id=agent_id,
            action='insight_published',
            resource_type='insight',
            resource_id=insight_id,
            details={'tags': tags, 'insight_type': insight_type, 'confidence': confidence}
        )

        # Update agent last_active timestamp
        self.pg_store.update_agent_last_active(agent_id)

        return insight_id

    def add_relationship(
        self,
        source_id: str,
        target_id: str,
        relation_type: RelationType,
        metadata: Optional[Dict[str, Any]] = None
    ) -> None:
        """
        Add a custom relationship between insights or agents.

        Args:
            source_id: Source node ID
            target_id: Target node ID
            relation_type: Type of relationship (BUILDS_ON, LED_TO)
            metadata: Additional metadata
        """
        relationship = Relationship(
            source_id=source_id,
            target_id=target_id,
            relation_type=relation_type,
            metadata=metadata or {}
        )
        self.store.add_relationship(relationship)

    def query_by_tags(
        self,
        tags: List[str],
        requester_role: Optional[str] = None,
        requester_agent_id: Optional[str] = None,
        match_all: bool = False
    ) -> List[Dict[str, Any]]:
        """
        Query insights by tags.

        Args:
            tags: List of tags to search
            requester_role: Role of requester (for permission filtering)
            requester_agent_id: Agent ID of requester (for audit logging)
            match_all: If True, must match ALL tags. If False, match ANY.

        Returns:
            List of insight dictionaries
        """
        insight_ids = self.store.get_insights_by_tags(tags, match_all)
        insights = [self.store.get_node(iid) for iid in insight_ids]
        insights = [{"id": iid, **ins} for iid, ins in zip(insight_ids, insights) if ins]

        # Filter by permissions
        if requester_role:
            insights = self._filter_by_permissions(insights, requester_role)

        # Audit log the query
        if requester_agent_id:
            self.pg_store.log_action(
                agent_id=requester_agent_id,
                action='query_by_tags',
                resource_type='insight',
                details={'tags': tags, 'match_all': match_all, 'results_count': len(insights)}
            )

        return insights

    def query_by_agent(
        self,
        agent_id: str,
        requester_role: Optional[str] = None,
        requester_agent_id: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """
        Query insights created by a specific agent.

        Args:
            agent_id: Agent ID
            requester_role: Role of requester (for permission filtering)
            requester_agent_id: Agent ID of requester (for audit logging)

        Returns:
            List of insight dictionaries
        """
        insight_ids = self.store.get_insights_by_agent(agent_id)
        insights = [self.store.get_node(iid) for iid in insight_ids]
        insights = [{"id": iid, **ins} for iid, ins in zip(insight_ids, insights) if ins]

        # Filter by permissions
        if requester_role:
            insights = self._filter_by_permissions(insights, requester_role)

        # Audit log the query
        if requester_agent_id:
            self.pg_store.log_action(
                agent_id=requester_agent_id,
                action='query_by_agent',
                resource_type='insight',
                details={'target_agent_id': agent_id, 'results_count': len(insights)}
            )

        return insights

    def query_by_time(
        self,
        start_date: str,
        end_date: Optional[str] = None,
        requester_role: Optional[str] = None,
        requester_agent_id: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """
        Query insights by time range.

        Args:
            start_date: Start date (YYYY-MM-DD)
            end_date: End date (YYYY-MM-DD), defaults to start_date
            requester_role: Role of requester (for permission filtering)
            requester_agent_id: Agent ID of requester (for audit logging)

        Returns:
            List of insight dictionaries
        """
        if end_date is None:
            end_date = start_date

        # Get all insights in date range
        all_insight_ids = set()
        current_date = start_date
        while current_date <= end_date:
            all_insight_ids.update(self.store.get_insights_by_date(current_date))
            # Move to next day (simplified - just for demo)
            current_date = self._increment_date(current_date)
            if current_date > end_date:
                break

        insights = [self.store.get_node(iid) for iid in all_insight_ids]
        insights = [{"id": iid, **ins} for iid, ins in zip(all_insight_ids, insights) if ins]

        # Filter by permissions
        if requester_role:
            insights = self._filter_by_permissions(insights, requester_role)

        # Audit log the query
        if requester_agent_id:
            self.pg_store.log_action(
                agent_id=requester_agent_id,
                action='query_by_time',
                resource_type='insight',
                details={'start_date': start_date, 'end_date': end_date, 'results_count': len(insights)}
            )

        return insights

    def get_insight_relationships(
        self,
        insight_id: str,
        relation_type: Optional[RelationType] = None,
        direction: str = "both"
    ) -> List[Dict[str, Any]]:
        """
        Get relationships for an insight.

        Args:
            insight_id: Insight ID
            relation_type: Filter by relationship type
            direction: "outgoing", "incoming", or "both"

        Returns:
            List of relationship dictionaries
        """
        return self.store.get_relationships(insight_id, relation_type, direction)

    def get_agent_influence(self, agent_id: str) -> Dict[str, Any]:
        """
        Get influence metrics for an agent.

        Shows how many insights reference this agent's insights (BUILDS_ON, LED_TO).

        Args:
            agent_id: Agent ID

        Returns:
            Dictionary with influence metrics
        """
        insights = self.store.get_insights_by_agent(agent_id)

        # Count relationship types
        builds_on_count = 0
        led_to_count = 0

        for insight_id in insights:
            relationships = self.store.get_relationships(
                insight_id,
                direction="incoming"
            )

            for rel in relationships:
                if rel["relation_type"] == RelationType.BUILDS_ON.value:
                    builds_on_count += 1
                elif rel["relation_type"] == RelationType.LED_TO.value:
                    led_to_count += 1

        return {
            "agent_id": agent_id,
            "insights_published": len(insights),
            "builds_on_count": builds_on_count,
            "led_to_count": led_to_count,
            "influenced_count": builds_on_count + led_to_count
        }

    def get_all_agents(self) -> List[Dict[str, Any]]:
        """Get all registered agents."""
        return self.store.get_nodes_by_type("agent")

    def get_all_topics(self) -> List[Dict[str, Any]]:
        """Get all topics."""
        return self.store.get_nodes_by_type("topic")

    def get_stats(self) -> Dict[str, Any]:
        """Get mesh statistics."""
        return self.store.get_stats()

    def save(self) -> None:
        """Save mesh to disk."""
        self.store.save()

    def _ensure_topic(self, tag: str) -> str:
        """
        Ensure a topic node exists for a tag.

        Args:
            tag: Tag name

        Returns:
            Topic ID
        """
        topic_id = f"topic_{tag}"

        if not self.store.get_node(topic_id):
            topic = Topic(name=tag, popularity=1)
            return self.store.add_topic_node(topic)
        else:
            # Increment popularity
            node = self.store.get_node(topic_id)
            node["popularity"] = node.get("popularity", 0) + 1
            return topic_id

    def _filter_by_permissions(
        self,
        insights: List[Dict[str, Any]],
        requester_role: str
    ) -> List[Dict[str, Any]]:
        """
        Filter insights by permissions using PostgreSQL.

        Permissions are derived from the agent's role in PostgreSQL, not stored in insights.

        Logic:
        1. Get requester's accessible roles from PostgreSQL (e.g., marketing can access ['marketing', 'sales'])
        2. For each insight, get the creator agent's role from PostgreSQL
        3. If creator's role is in requester's accessible roles, allow access

        Args:
            insights: List of insights
            requester_role: Role of requester

        Returns:
            Filtered list of insights
        """
        # Get what roles the requester can access from PostgreSQL
        requester_role_data = self.pg_store.get_role(requester_role)
        if not requester_role_data:
            # Role doesn't exist, deny all
            return []

        accessible_roles = requester_role_data['can_access_roles']

        # Filter insights: keep only those created by agents with accessible roles
        filtered_insights = []
        for insight in insights:
            # Get the agent who created this insight
            creator_agent_id = insight.get('agent_id')
            if not creator_agent_id:
                continue

            # Get creator agent's role from PostgreSQL
            creator_agent = self.pg_store.get_agent(creator_agent_id)
            if not creator_agent:
                continue

            creator_role = creator_agent['role']

            # Check if creator's role is in accessible roles
            if creator_role in accessible_roles:
                filtered_insights.append(insight)

        return filtered_insights

    def _increment_date(self, date_str: str) -> str:
        """
        Increment date by one day (simplified).

        Args:
            date_str: Date string (YYYY-MM-DD)

        Returns:
            Next day date string
        """
        from datetime import datetime, timedelta
        date_obj = datetime.strptime(date_str, "%Y-%m-%d")
        next_day = date_obj + timedelta(days=1)
        return next_day.strftime("%Y-%m-%d")
