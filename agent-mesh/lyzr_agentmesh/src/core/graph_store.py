"""
Graph storage layer using NetworkX.

Manages the NetworkX graph, indexing, and persistence.
"""

import networkx as nx
import pickle
from typing import Dict, List, Set, Optional, Any
from collections import defaultdict
from pathlib import Path

from lyzr_agentmesh.src.models.data_models import Agent, Insight, Topic, Relationship, RelationType

class GraphStore:
    """
    Manages the NetworkX graph and auxiliary indexes for fast lookups.
    """

    def __init__(self, persist_path: Optional[str] = None):
        """
        Initialize the graph store.

        Args:
            persist_path: Optional path to save/load graph from disk
        """
        self.graph = nx.DiGraph()
        self.persist_path = persist_path

        # Auxiliary indexes for fast lookups
        self.tag_index: Dict[str, Set[str]] = defaultdict(set)
        self.agent_index: Dict[str, Set[str]] = defaultdict(set)
        self.time_index: Dict[str, Set[str]] = defaultdict(set)  # date -> insight_ids
        self.type_index: Dict[str, Set[str]] = defaultdict(set)  # node_type -> node_ids

        # Load from disk if exists
        if persist_path and Path(persist_path).exists():
            self.load()

    def add_agent_node(self, agent: Agent) -> str:
        """
        Add an agent node to the graph.

        Args:
            agent: Agent object

        Returns:
            Agent ID
        """
        self.graph.add_node(
            agent.agent_id,
            node_type="agent",
            framework=agent.framework,
            role=agent.role,
            # permissions=agent.permissions,
            metadata=agent.metadata
        )

        # Update indexes
        self.type_index["agent"].add(agent.agent_id)

        return agent.agent_id

    def add_insight_node(self, insight: Insight) -> str:
        """
        Add an insight node to the graph.

        Args:
            insight: Insight object

        Returns:
            Insight ID
        """
        self.graph.add_node(
            insight.id,
            node_type="insight",
            agent_id=insight.agent_id,
            observation=insight.observation,
            timestamp=insight.timestamp,
            tags=insight.tags,
            # permissions=insight.permissions,
            context=insight.context,
            insight_type=insight.insight_type,
            confidence=insight.confidence
        )

        # Update indexes
        self.type_index["insight"].add(insight.id)
        self.agent_index[insight.agent_id].add(insight.id)

        for tag in insight.tags:
            self.tag_index[tag].add(insight.id)

        # Index by date (YYYY-MM-DD)
        date = insight.timestamp.split('T')[0]
        self.time_index[date].add(insight.id)

        return insight.id

    def add_topic_node(self, topic: Topic) -> str:
        """
        Add a topic node to the graph.

        Args:
            topic: Topic object

        Returns:
            Topic ID (name)
        """
        topic_id = f"topic_{topic.name}"

        if not self.graph.has_node(topic_id):
            self.graph.add_node(
                topic_id,
                node_type="topic",
                name=topic.name,
                popularity=topic.popularity,
                metadata=topic.metadata
            )
            self.type_index["topic"].add(topic_id)
        else:
            # Update popularity if topic exists
            self.graph.nodes[topic_id]["popularity"] = topic.popularity

        return topic_id

    def add_relationship(self, relationship: Relationship) -> None:
        """
        Add a relationship (edge) between nodes.

        Args:
            relationship: Relationship object
        """
        self.graph.add_edge(
            relationship.source_id,
            relationship.target_id,
            relation_type=relationship.relation_type.value,
            metadata=relationship.metadata,
            timestamp=relationship.timestamp
        )

    def get_node(self, node_id: str) -> Optional[Dict[str, Any]]:
        """
        Get a node by ID.

        Args:
            node_id: Node ID

        Returns:
            Node attributes or None if not found
        """
        if self.graph.has_node(node_id):
            return dict(self.graph.nodes[node_id])
        return None

    def get_nodes_by_type(self, node_type: str) -> List[Dict[str, Any]]:
        """
        Get all nodes of a specific type.

        Args:
            node_type: Type of node (agent, insight, topic)

        Returns:
            List of node dictionaries with id
        """
        node_ids = self.type_index.get(node_type, set())
        return [
            {"id": node_id, **self.graph.nodes[node_id]}
            for node_id in node_ids
        ]

    def get_insights_by_tags(self, tags: List[str], match_all: bool = False) -> List[str]:
        """
        Get insight IDs by tags.

        Args:
            tags: List of tags to search
            match_all: If True, insight must have ALL tags. If False, ANY tag.

        Returns:
            List of insight IDs
        """
        if not tags:
            return []

        if match_all:
            # Intersection - must have all tags
            result = self.tag_index.get(tags[0], set()).copy()
            for tag in tags[1:]:
                result &= self.tag_index.get(tag, set())
            return list(result)
        else:
            # Union - has any tag
            result = set()
            for tag in tags:
                result |= self.tag_index.get(tag, set())
            return list(result)

    def get_insights_by_agent(self, agent_id: str) -> List[str]:
        """
        Get insight IDs created by an agent.

        Args:
            agent_id: Agent ID

        Returns:
            List of insight IDs
        """
        return list(self.agent_index.get(agent_id, set()))

    def get_insights_by_date(self, date: str) -> List[str]:
        """
        Get insight IDs by date.

        Args:
            date: Date string (YYYY-MM-DD)

        Returns:
            List of insight IDs
        """
        return list(self.time_index.get(date, set()))

    def get_relationships(
        self,
        node_id: str,
        relation_type: Optional[RelationType] = None,
        direction: str = "outgoing"
    ) -> List[Dict[str, Any]]:
        """
        Get relationships for a node.

        Args:
            node_id: Node ID
            relation_type: Filter by relationship type
            direction: "outgoing", "incoming", or "both"

        Returns:
            List of relationship dictionaries
        """
        relationships = []

        if direction in ["outgoing", "both"]:
            for target in self.graph.successors(node_id):
                edge_data = self.graph.edges[node_id, target]
                if relation_type is None or edge_data["relation_type"] == relation_type.value:
                    relationships.append({
                        "source": node_id,
                        "target": target,
                        **edge_data
                    })

        if direction in ["incoming", "both"]:
            for source in self.graph.predecessors(node_id):
                edge_data = self.graph.edges[source, node_id]
                if relation_type is None or edge_data["relation_type"] == relation_type.value:
                    relationships.append({
                        "source": source,
                        "target": node_id,
                        **edge_data
                    })

        return relationships

    def rebuild_indexes(self) -> None:
        """Rebuild all auxiliary indexes from the graph."""
        self.tag_index.clear()
        self.agent_index.clear()
        self.time_index.clear()
        self.type_index.clear()

        for node_id, data in self.graph.nodes(data=True):
            node_type = data.get("node_type")

            # Type index
            if node_type:
                self.type_index[node_type].add(node_id)

            # Insight-specific indexes
            if node_type == "insight":
                # Agent index
                agent_id = data.get("agent_id")
                if agent_id:
                    self.agent_index[agent_id].add(node_id)

                # Tag index
                tags = data.get("tags", [])
                for tag in tags:
                    self.tag_index[tag].add(node_id)

                # Time index
                timestamp = data.get("timestamp", "")
                if timestamp:
                    date = timestamp.split('T')[0]
                    self.time_index[date].add(node_id)

    def save(self, path: Optional[str] = None) -> None:
        """
        Save graph to disk using pickle.

        Args:
            path: Path to save to (defaults to self.persist_path)
        """
        save_path = path or self.persist_path
        if not save_path:
            raise ValueError("No persist_path specified")

        with open(save_path, 'wb') as f:
            pickle.dump(self.graph, f)

    def load(self, path: Optional[str] = None) -> None:
        """
        Load graph from disk.

        Args:
            path: Path to load from (defaults to self.persist_path)
        """
        load_path = path or self.persist_path
        if not load_path:
            raise ValueError("No persist_path specified")

        with open(load_path, 'rb') as f:
            self.graph = pickle.load(f)

        # Rebuild indexes after loading
        self.rebuild_indexes()

    def get_stats(self) -> Dict[str, Any]:
        """Get statistics about the graph."""
        return {
            "total_nodes": self.graph.number_of_nodes(),
            "total_edges": self.graph.number_of_edges(),
            "agents": len(self.type_index.get("agent", set())),
            "insights": len(self.type_index.get("insight", set())),
            "topics": len(self.type_index.get("topic", set())),
            "unique_tags": len(self.tag_index)
        }
