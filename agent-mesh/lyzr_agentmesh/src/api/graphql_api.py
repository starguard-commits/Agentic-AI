"""
GraphQL API wrapper for AgentMesh.

Provides a simple interface to interact with the mesh via GraphQL.
"""

from typing import Dict, Any

from lyzr_agentmesh.src.api.resolvers import create_schema, execute_query
from lyzr_agentmesh.src.core.mesh import AgentMesh


class GraphQLAPI:
    """
    GraphQL API wrapper for AgentMesh.

    Provides easy access to GraphQL queries without manually creating schema.
    """

    def __init__(self, mesh: AgentMesh):
        """
        Initialize GraphQL API.

        Args:
            mesh: AgentMesh instance
        """
        self.mesh = mesh
        self.schema = create_schema(mesh)

    def query(self, query_string: str) -> Dict[str, Any]:
        """
        Execute a GraphQL query.

        Args:
            query_string: GraphQL query

        Returns:
            Query result with 'data' and 'errors' keys

        Example:
            >>> api = GraphQLAPI(mesh)
            >>> result = api.query('''
            ...     query {
            ...         agents {
            ...             id
            ...             role
            ...         }
            ...     }
            ... ''')
            >>> print(result['data'])
        """
        return execute_query(self.schema, query_string)

    def get_agents(self) -> Dict[str, Any]:
        """
        Get all agents via GraphQL.

        Note: Permissions are not returned - they are managed in PostgreSQL
        and derived based on the agent's role.
        """
        return self.query('''
            query {
                agents {
                    id
                    framework
                    role
                }
            }
        ''')

    def get_insights_by_tags(self, tags: list, role: str = None) -> Dict[str, Any]:
        """
        Get insights by tags via GraphQL.

        Args:
            tags: List of tags
            role: Optional role for permission filtering

        Returns:
            Query result
        """
        tags_str = str(tags).replace("'", '"')
        role_arg = f', role: "{role}"' if role else ''

        query = f'''
            query {{
                insightsByTags(tags: {tags_str}{role_arg}) {{
                    id
                    observation
                    tags
                    timestamp
                    agentId
                }}
            }}
        '''
        return self.query(query)

    def get_agent_influence(self, agent_id: str) -> Dict[str, Any]:
        """
        Get agent influence metrics via GraphQL.

        Args:
            agent_id: Agent ID

        Returns:
            Query result
        """
        return self.query(f'''
            query {{
                agentInfluence(agentId: "{agent_id}") {{
                    agentId
                    insightsPublished
                    accessedByAgents
                    influencedCount
                    buildsOnCount
                    ledToCount
                }}
            }}
        ''')

    def get_mesh_stats(self) -> Dict[str, Any]:
        """Get mesh statistics via GraphQL."""
        return self.query('''
            query {
                meshStats {
                    totalNodes
                    totalEdges
                    agents
                    insights
                    topics
                    uniqueTags
                }
            }
        ''')
