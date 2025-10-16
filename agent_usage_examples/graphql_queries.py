"""
GraphQL query agent_usage_examples for AgentMesh.

Demonstrates various GraphQL queries against the mesh.

Prerequisites:
    pip install agentmesh-1.0.0.tar.gz
    createdb agentmesh
"""

import json

from lyzr_agentmesh.src.core.mesh import AgentMesh
from lyzr_agentmesh.src.adapters import AgentMeshAdapter
from lyzr_agentmesh.src.api import GraphQLAPI


def print_result(title: str, result: dict):
    """Pretty print a GraphQL result."""
    print(f"\n{title}")
    print("-" * 60)
    if result.get('errors'):
        print(f"❌ Errors: {result['errors']}")
    else:
        print(json.dumps(result['data'], indent=2))


def main():
    print("=" * 70)
    print("AgentMesh - GraphQL Query Examples")
    print("=" * 70)

    # Setup mesh with some data (with mandatory PostgreSQL)
    mesh = AgentMesh(
        persist_path="graphql_demo.pkl",
        pg_config={
            'host': 'localhost',
            'port': 5432,
            'database': 'agentmesh',
            'user': 'postgres',
            'password': 'postgres'
        }
    )

    # Create agents and publish insights
    sales = AgentMeshAdapter("sales_001", mesh, "mock", "sales")
    marketing = AgentMeshAdapter("marketing_001", mesh, "mock", "marketing")
    # Note: Permissions now managed via roles in PostgreSQL

    sales.publish_insight("Customer wants bulk pricing", ["pricing", "bulk"])
    sales.publish_insight("High interest in laptops", ["product", "laptop"])
    campaign_id = marketing.publish_insight("Laptop promotion campaign", ["campaign", "laptop"])

    # Create GraphQL API
    api = GraphQLAPI(mesh)

    # Example 1: Get all agents
    print_result(
        "Query 1: Get All Agents",
        api.query('''
            query {
                agents {
                    id
                    role
                    framework
                    permissions
                }
            }
        ''')
    )

    # Example 2: Get insights by tags
    print_result(
        "Query 2: Get Insights Tagged 'laptop' (as sales role)",
        api.query('''
            query {
                insightsByTags(tags: ["laptop"], role: "sales") {
                    id
                    observation
                    tags
                    agentId
                }
            }
        ''')
    )

    # Example 3: Get insights by agent
    print_result(
        "Query 3: Get Insights from Sales Agent",
        api.query('''
            query {
                insightsByAgent(agentId: "sales_001", role: "sales") {
                    id
                    observation
                    timestamp
                    tags
                }
            }
        ''')
    )

    # Example 4: Get agent influence
    print_result(
        "Query 4: Get Sales Agent Influence",
        api.query('''
            query {
                agentInfluence(agentId: "sales_001") {
                    agentId
                    insightsPublished
                    influencedCount
                }
            }
        ''')
    )

    # Example 5: Get mesh statistics
    print_result(
        "Query 5: Get Mesh Statistics",
        api.query('''
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
    )

    # Example 6: Get all topics
    print_result(
        "Query 6: Get All Topics",
        api.query('''
            query {
                topics {
                    id
                    name
                    popularity
                }
            }
        ''')
    )

    # Example 7: Complex query - multiple tags with match all
    print_result(
        "Query 7: Get Insights Tagged with BOTH 'laptop' AND 'campaign'",
        api.query('''
            query {
                insightsByTags(tags: ["laptop", "campaign"], matchAll: true, role: "marketing") {
                    id
                    observation
                    tags
                }
            }
        ''')
    )

    print("\n" + "=" * 70)
    print("✅ GraphQL agent_usage_examples completed!")
    print("=" * 70)


if __name__ == "__main__":
    main()
