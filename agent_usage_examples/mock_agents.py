"""
Mock agents example for AgentMesh.

Demonstrates a realistic e-commerce scenario with 3 agents:
- Sales Agent: Tracks customer inquiries
- Marketing Agent: Creates campaigns based on customer trends
- Inventory Agent: Adjusts stock based on demand

Now uses @publish_to_mesh decorator for simplified integration!

Prerequisites:
    pip install agentmesh-1.0.0.tar.gz
    createdb agentmesh
"""

from lyzr_agentmesh.src.core.mesh import AgentMesh
from lyzr_agentmesh.src.adapters import AgentMeshAdapter
from lyzr_agentmesh.src.decorators import publish_to_mesh

class MockSalesAgent:
    """Mock sales agent that tracks customer inquiries (using decorator!)."""

    def __init__(self, agent_id: str, mesh: AgentMesh):
        """
        Initialize sales agent.

        Args:
            agent_id: Agent identifier
            mesh: AgentMesh instance
        """
        self.adapter = AgentMeshAdapter(
            agent_id=agent_id,
            mesh=mesh,
            framework="mock",
            role="sales"
        )
        self.name = "Sales Agent"

    @publish_to_mesh(
        observation="{count} customer(s) inquired about {inquiry_type} for {product}",
        tags=["customer_inquiry", "{inquiry_type}", "{product}"],
        context=["product", "inquiry_type", "count"]
    )
    def log_customer_inquiry(self, product: str, inquiry_type: str, count: int = 1):
        """
        Log a customer inquiry (decorator auto-publishes!).

        Args:
            product: Product name
            inquiry_type: Type of inquiry
            count: Number of inquiries
        """
        pass  # Decorator handles everything!

    @publish_to_mesh(
        observation="{observation}",
        tags=["{tags}"],  # Expands the tags list parameter!
        insight_type="pattern",
        context=False
    )
    def log_sales_trend(self, observation: str, tags: list):
        """Log a sales trend observation (decorator auto-publishes, even with dynamic tags!)."""
        pass  # Decorator handles everything, including list expansion!


class MockMarketingAgent:
    """Mock marketing agent that creates campaigns (using decorator!)."""

    def __init__(self, agent_id: str, mesh: AgentMesh):
        """
        Initialize marketing agent.

        Args:
            agent_id: Agent identifier
            mesh: AgentMesh instance
        """
        self.adapter = AgentMeshAdapter(
            agent_id=agent_id,
            mesh=mesh,
            framework="mock",
            role="marketing",
        )
        self.name = "Marketing Agent"

    def analyze_customer_trends(self):
        """
        Analyze customer trends by querying sales insights.

        Returns:
            List of insights
        """
        # Query insights from sales
        insights = self.adapter.query_by_tags(["customer_inquiry"])
        return insights

    @publish_to_mesh(
        observation="Launched '{campaign_name}' campaign targeting {target} customers",
        tags=["campaign", "{target}", "marketing_action"],
        insight_type="action",
        context=["campaign_name", "target"],
        builds_on="based_on_insights"  # Auto-creates BUILDS_ON relationships!
    )
    def create_campaign(self, campaign_name: str, target: str, based_on_insights: list):
        """
        Create a marketing campaign based on insights (decorator auto-publishes!).

        Args:
            campaign_name: Campaign name
            target: Target product/category
            based_on_insights: List of insight IDs this builds on

        Returns:
            Campaign insight ID
        """
        pass  # Decorator handles publishing AND relationship creation!


class MockInventoryAgent:
    """Mock inventory agent that manages stock (using decorator!)."""

    def __init__(self, agent_id: str, mesh: AgentMesh):
        """
        Initialize inventory agent.

        Args:
            agent_id: Agent identifier
            mesh: AgentMesh instance
        """
        self.adapter = AgentMeshAdapter(
            agent_id=agent_id,
            mesh=mesh,
            framework="mock",
            role="inventory"
            # Note: Permissions now managed via roles in PostgreSQL
            # Inventory role has access to sales and marketing insights
        )
        self.name = "Inventory Agent"

    def analyze_demand(self, product: str):
        """
        Analyze demand for a product by checking insights.

        Args:
            product: Product name

        Returns:
            List of relevant insights
        """
        # Query insights about this product
        insights = self.adapter.query_by_tags([product.lower()])
        return insights

    @publish_to_mesh(
        observation="Inventory decision: {action} {quantity} units of {product}",
        tags=["inventory_decision", "{product}", "{action}"],
        insight_type="decision",
        context=["product", "action", "quantity"],
        led_to_by="reason_insights"  # Auto-creates LED_TO relationships!
    )
    def adjust_stock(self, product: str, action: str, quantity: int, reason_insights: list):
        """
        Adjust stock levels based on demand (decorator auto-publishes!).

        Args:
            product: Product name
            action: Action taken (order, reduce, etc.)
            quantity: Quantity adjustment
            reason_insights: Insights that led to this decision

        Returns:
            Decision insight ID
        """
        pass  # Decorator handles publishing AND LED_TO relationship creation!


def run_scenario():
    """Run the e-commerce scenario."""
    print("=" * 70)
    print("AgentMesh - E-commerce Multi-Agent Scenario")
    print("=" * 70)
    print()

    # Initialize mesh (with mandatory PostgreSQL)
    print("🔧 Connecting to PostgreSQL...")
    mesh = AgentMesh(
        persist_path="ecommerce_mesh.pkl",
        pg_config={
            'host': 'localhost',
            'port': 5432,
            'database': 'agentmesh',
            'user': 'postgres',
            'password': 'postgres'
        }
    )
    print("✓ AgentMesh initialized with PostgreSQL integration")
    print()

    # Create agents
    sales = MockSalesAgent("sales_001", mesh)
    marketing = MockMarketingAgent("marketing_001", mesh)
    inventory = MockInventoryAgent("inventory_001", mesh)

    print("📊 Agents initialized:")
    print(f"   - {sales.name}")
    print(f"   - {marketing.name}")
    print(f"   - {inventory.name}")
    print()

    # Day 1: Sales logs customer inquiries
    print("📅 Day 1: Sales agent logs customer inquiries")
    print("-" * 70)

    insight1 = sales.log_customer_inquiry("laptops", "bulk_pricing", count=5)
    print(f"   ✓ Logged: 5 customers asked about bulk laptop pricing")

    insight2 = sales.log_customer_inquiry("laptops", "gaming_specs", count=3)
    print(f"   ✓ Logged: 3 customers asked about gaming laptop specs")

    insight3 = sales.log_sales_trend(
        "Increasing interest in high-performance laptops",
        ["trend", "laptops", "high_demand"]
    )
    print(f"   ✓ Logged: Sales trend - high-performance laptops in demand")
    print()

    # Day 2: Marketing analyzes trends and creates campaign
    print("📅 Day 2: Marketing agent analyzes trends")
    print("-" * 70)

    trends = marketing.analyze_customer_trends()
    print(f"   ✓ Found {len(trends)} customer insights")
    print(f"   ✓ Analysis: Strong interest in laptops")
    print()

    print("   💡 Creating campaign based on insights...")
    campaign_id = marketing.create_campaign(
        campaign_name="Laptop Mega Sale",
        target="laptop",
        based_on_insights=[insight1, insight2, insight3]
    )
    print(f"   ✓ Campaign launched: 'Laptop Mega Sale'")
    print(f"   ✓ Campaign BUILDS_ON {len([insight1, insight2, insight3])} sales insights")
    print()

    # Day 3: Inventory adjusts stock
    print("📅 Day 3: Inventory agent analyzes demand")
    print("-" * 70)

    demand_insights = inventory.analyze_demand("laptops")
    print(f"   ✓ Found {len(demand_insights)} insights about laptops")
    print(f"   ✓ Analysis: High demand + marketing campaign active")
    print()

    print("   📦 Making inventory decision...")
    decision_id = inventory.adjust_stock(
        product="laptops",
        action="order",
        quantity=50,
        reason_insights=[insight1, insight2, insight3, campaign_id]
    )
    print(f"   ✓ Decision: Order 50 more laptops")
    print(f"   ✓ Decision LED_TO by {len([insight1, insight2, insight3, campaign_id])} insights")
    print()

    # Show influence
    print("📈 Agent Influence Metrics")
    print("-" * 70)

    sales_influence = sales.adapter.get_my_influence()
    print(f"   {sales.name}:")
    print(f"      - Published: {sales_influence['insights_published']} insights")
    print(f"      - Influenced: {sales_influence['influenced_count']} agents")
    print(f"      - Led to: {sales_influence['led_to_count']} decisions")
    print()

    marketing_influence = marketing.adapter.get_my_influence()
    print(f"   {marketing.name}:")
    print(f"      - Published: {marketing_influence['insights_published']} insights")
    print(f"      - Builds on: {marketing_influence['builds_on_count']} other insights")
    print()

    # Show mesh stats
    print("📊 Mesh Statistics")
    print("-" * 70)
    stats = mesh.get_stats()
    print(f"   Total Agents: {stats['agents']}")
    print(f"   Total Insights: {stats['insights']}")
    print(f"   Total Topics: {stats['topics']}")
    print(f"   Unique Tags: {stats['unique_tags']}")
    print()

    # Save mesh
    mesh.save()
    print("💾 Mesh saved to ecommerce_mesh.pkl")
    print()

    print("=" * 70)
    print("✅ Scenario completed successfully!")
    print()
    print("Key Takeaway:")
    print("   Sales insights → Marketing campaigns → Inventory decisions")
    print("   Collective intelligence enables better organizational decisions")
    print("=" * 70)


if __name__ == "__main__":
    run_scenario()
