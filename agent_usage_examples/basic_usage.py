"""
Basic usage example for AgentMesh.

Demonstrates the fundamental operations:
- Creating a mesh
- Registering agents
- Publishing insights
- Querying insights
- Creating relationships

Prerequisites:
    pip install agentmesh-1.0.0.tar.gz
    createdb agentmesh
"""
from lyzr_agentmesh.src.core.mesh import AgentMesh
from lyzr_agentmesh.src.adapters import AgentMeshAdapter
from lyzr_agentmesh.src.api import GraphQLAPI

def main():
    print("=" * 60)
    print("AgentMesh - Basic Usage Example")
    print("=" * 60)
    print()

    # 1. Create mesh (with mandatory PostgreSQL)
    print("1. Creating AgentMesh...")
    print("   Note: Connecting to PostgreSQL (localhost:5432/agentmesh)...")
    mesh = AgentMesh(
        persist_path="demo_mesh.pkl",
        pg_config={
            'host': 'localhost',
            'port': 5432,
            'database': 'agentmesh',
            'user': 'postgres',
            'password': 'postgres'
        }
    )
    print(f"   ✓ Mesh created with PostgreSQL integration")
    print()

    # 2. Create adapters (auto-registers agents)
    print("2. Creating agent adapters...")
    sales_adapter = AgentMeshAdapter(
        agent_id="sales_001",
        mesh=mesh,
        framework="mock",
        role="sales"
    )
    print(f"   ✓ Sales agent adapter created (auto-registered)")

    marketing_adapter = AgentMeshAdapter(
        agent_id="marketing_001",
        mesh=mesh,
        framework="mock",
        role="marketing"
        # Note: Permissions now managed via roles in PostgreSQL
    )
    print(f"   ✓ Marketing agent adapter created (auto-registered)")
    print()

    # 3. Publish insights
    print("3. Publishing insights...")
    insight1_id = sales_adapter.publish_insight(
        observation="Customer inquiry: 5 customers asked about bulk laptop pricing today",
        tags=["pricing", "bulk", "laptop", "customer_interest"]
    )
    print(f"   ✓ Sales insight published: {insight1_id[:8]}...")

    insight2_id = sales_adapter.publish_insight(
        observation="High interest in gaming laptops with dedicated GPUs",
        tags=["product_interest", "laptop", "gaming"],
        context={"urgency": "high"}
    )
    print(f"   ✓ Sales insight published: {insight2_id[:8]}...")

    insight3_id = marketing_adapter.publish_insight(
        observation="Launched 'Back to School' laptop promotion campaign",
        tags=["campaign", "laptop", "promotion"]
    )
    print(f"   ✓ Marketing insight published: {insight3_id[:8]}...")
    print()

    # 4. Create relationships
    print("4. Creating relationships...")
    marketing_adapter.add_relationship(
        source_id=insight3_id,
        target_id=insight1_id,
        relation_type="BUILDS_ON",
        metadata={"reason": "Campaign based on customer demand"}
    )
    print(f"   ✓ Marketing campaign BUILDS_ON sales insight")
    print()

    # 5. Query insights
    print("5. Querying insights...")

    # Query by tags
    laptop_insights = mesh.query_by_tags(
        tags=["laptop"],
        requester_role="sales"
    )
    print(f"   ✓ Found {len(laptop_insights)} insights tagged 'laptop'")

    # Query by agent
    sales_insights = mesh.query_by_agent(
        agent_id="sales_001",
        requester_role="sales"
    )
    print(f"   ✓ Found {len(sales_insights)} insights from sales agent")

    # Query relationships
    relationships = mesh.get_insight_relationships(insight3_id)
    print(f"   ✓ Found {len(relationships)} relationships for marketing campaign")
    print()

    # 6. Check agent influence
    print("6. Checking agent influence...")
    sales_influence = sales_adapter.get_my_influence()
    print(f"   ✓ Sales agent published: {sales_influence['insights_published']} insights")
    print(f"   ✓ Influenced: {sales_influence['influenced_count']} other agents")
    print()

    # 7. GraphQL queries
    print("7. Querying via GraphQL API...")
    api = GraphQLAPI(mesh)

    result = api.get_mesh_stats()
    if result['data']:
        stats = result['data']['meshStats']
        print(f"   ✓ Total agents: {stats['agents']}")
        print(f"   ✓ Total insights: {stats['insights']}")
        print(f"   ✓ Total topics: {stats['topics']}")
    print()

    # 8. Save mesh
    print("8. Saving mesh to disk...")
    mesh.save()
    print(f"   ✓ Mesh saved to demo_mesh.pkl")
    print()

    print("=" * 60)
    print("Basic usage example completed successfully!")
    print("=" * 60)


if __name__ == "__main__":
    main()
