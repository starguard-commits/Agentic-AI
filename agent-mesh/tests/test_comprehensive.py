"""
Comprehensive Test Suite for AgentMesh

Tests cover main functionality across all core components:
- Data models validation
- Core mesh operations (register, publish, query)
- PostgreSQL integration (agents, roles, permissions, audit)
- Access control and permission filtering
- Relationships (BUILDS_ON, LED_TO)
- Agent adapters
- Decorator-based publishing
- Graph operations and indexing

Requirements:
    - PostgreSQL database 'agentmesh_test' must exist
    - Run: createdb agentmesh_test
"""

import pytest
import tempfile
import os
from datetime import datetime

from agentmesh.src.core.mesh import AgentMesh
from agentmesh.src.adapters.mock_adapter import AgentMeshAdapter
from agentmesh.src.models.data_models import Agent, Insight, Topic, Relationship, RelationType
from agentmesh.src.decorators import publish_to_mesh


# ===========================
# Fixtures
# ===========================

@pytest.fixture
def test_mesh():
    """Create a temporary AgentMesh for testing."""
    with tempfile.TemporaryDirectory() as tmpdir:
        mesh_path = os.path.join(tmpdir, "test_mesh.pkl")

        # Use test database
        pg_config = {
            'host': 'localhost',
            'port': 5432,
            'database': 'agentmesh_test',
            'user': 'postgres',
            'password': 'postgres'
        }

        mesh = AgentMesh(persist_path=mesh_path, pg_config=pg_config)

        # Clean up test data
        yield mesh

        # Cleanup: Remove test agents
        try:
            mesh.pg_store.conn.execute("DELETE FROM agents WHERE id LIKE 'test_%'")
            mesh.pg_store.conn.commit()
        except:
            pass


@pytest.fixture
def sample_agents(test_mesh):
    """Register sample agents for testing."""
    agents = {
        'sales': test_mesh.register_agent('test_sales_001', 'mock', 'sales'),
        'marketing': test_mesh.register_agent('test_marketing_001', 'mock', 'marketing'),
        'inventory': test_mesh.register_agent('test_inventory_001', 'mock', 'inventory'),
        'executive': test_mesh.register_agent('test_executive_001', 'mock', 'executive')
    }
    return agents


# ===========================
# Test 1-4: Data Models Validation
# ===========================

def test_agent_model_validation():
    """Test 1: Agent model validation"""
    # Valid agent
    agent = Agent(agent_id="agent_001", framework="mock", role="sales")
    assert agent.agent_id == "agent_001"
    assert agent.framework == "mock"
    assert agent.role == "sales"

    # Invalid: missing agent_id
    with pytest.raises(ValueError, match="agent_id is required"):
        Agent(agent_id="", framework="mock", role="sales")

    # Invalid: missing role
    with pytest.raises(ValueError, match="role is required"):
        Agent(agent_id="agent_001", framework="mock", role="")


def test_insight_model_validation():
    """Test 2: Insight model validation"""
    # Valid insight
    insight = Insight(
        agent_id="agent_001",
        observation="Customer wants bulk pricing",
        tags=["pricing", "bulk"],
        confidence=0.95
    )
    assert insight.agent_id == "agent_001"
    assert insight.confidence == 0.95
    assert len(insight.tags) == 2

    # Invalid: missing agent_id
    with pytest.raises(ValueError, match="agent_id is required"):
        Insight(agent_id="", observation="Test")

    # Invalid: missing observation
    with pytest.raises(ValueError, match="observation is required"):
        Insight(agent_id="agent_001", observation="")

    # Invalid: confidence out of range
    with pytest.raises(ValueError, match="confidence must be between 0 and 1"):
        Insight(agent_id="agent_001", observation="Test", confidence=1.5)


def test_topic_model_validation():
    """Test 3: Topic model validation"""
    # Valid topic
    topic = Topic(name="pricing", popularity=10)
    assert topic.name == "pricing"
    assert topic.popularity == 10

    # Invalid: missing name
    with pytest.raises(ValueError, match="name is required"):
        Topic(name="")


def test_relationship_model_validation():
    """Test 4: Relationship model validation"""
    # Valid relationship
    rel = Relationship(
        source_id="insight_001",
        target_id="insight_002",
        relation_type=RelationType.BUILDS_ON
    )
    assert rel.source_id == "insight_001"
    assert rel.relation_type == RelationType.BUILDS_ON

    # Invalid: missing source_id
    with pytest.raises(ValueError, match="source_id is required"):
        Relationship(source_id="", target_id="insight_002", relation_type=RelationType.BUILDS_ON)


# ===========================
# Test 5-8: Core Mesh Operations
# ===========================

def test_register_agent(test_mesh):
    """Test 5: Register agent in mesh"""
    agent_id = test_mesh.register_agent(
        agent_id="test_agent_001",
        framework="langchain",
        role="sales",
        metadata={"version": "1.0"}
    )

    assert agent_id == "test_agent_001"

    # Verify in PostgreSQL
    pg_agent = test_mesh.pg_store.get_agent("test_agent_001")
    assert pg_agent['framework'] == "langchain"
    assert pg_agent['role'] == "sales"

    # Verify in NetworkX
    graph_agent = test_mesh.store.get_node("test_agent_001")
    assert graph_agent['framework'] == "langchain"


def test_publish_insight(test_mesh, sample_agents):
    """Test 6: Publish insight to mesh"""
    insight_id = test_mesh.publish_insight(
        agent_id="test_sales_001",
        observation="5 customers inquired about laptops",
        tags=["inquiry", "laptop"],
        context={"product": "laptop", "count": 5},
        insight_type="observation",
        confidence=1.0
    )

    assert insight_id is not None

    # Verify insight stored
    insight = test_mesh.store.get_node(insight_id)
    assert insight['observation'] == "5 customers inquired about laptops"
    assert insight['agent_id'] == "test_sales_001"
    assert "laptop" in insight['tags']

    # Verify CREATED relationship exists
    relationships = test_mesh.get_insight_relationships(insight_id, direction="incoming")
    created_rels = [r for r in relationships if r['relation_type'] == 'CREATED']
    assert len(created_rels) == 1
    assert created_rels[0]['source_id'] == "test_sales_001"


def test_query_by_tags(test_mesh, sample_agents):
    """Test 7: Query insights by tags"""
    # Publish insights
    test_mesh.publish_insight("test_sales_001", "Laptop inquiry", ["laptop", "inquiry"], confidence=1.0)
    test_mesh.publish_insight("test_sales_001", "Bulk pricing request", ["laptop", "pricing"], confidence=1.0)
    test_mesh.publish_insight("test_marketing_001", "Campaign performance", ["campaign"], confidence=1.0)

    # Query by single tag
    results = test_mesh.query_by_tags(["laptop"], requester_role="sales")
    assert len(results) >= 2

    # Query with match_all=True
    results = test_mesh.query_by_tags(["laptop", "pricing"], requester_role="sales", match_all=True)
    assert len(results) >= 1
    assert any("pricing" in r['tags'] for r in results)


def test_query_with_permission_filtering(test_mesh, sample_agents):
    """Test 8: Query with role-based permission filtering"""
    # Sales publishes insight
    sales_insight = test_mesh.publish_insight(
        "test_sales_001",
        "Customer wants bulk pricing",
        ["pricing"],
        confidence=1.0
    )

    # Marketing publishes insight
    marketing_insight = test_mesh.publish_insight(
        "test_marketing_001",
        "Campaign launched",
        ["campaign"],
        confidence=1.0
    )

    # Sales agent queries (can only see sales insights)
    results = test_mesh.query_by_tags(["pricing"], requester_role="sales")
    assert len(results) == 1
    assert results[0]['id'] == sales_insight

    # Marketing agent queries pricing (can see sales + marketing due to role hierarchy)
    results = test_mesh.query_by_tags(["pricing"], requester_role="marketing")
    assert len(results) == 1  # Can see sales insights

    # Executive queries (can see all)
    all_results = test_mesh.query_by_tags(["pricing", "campaign"], requester_role="executive", match_all=False)
    assert len(all_results) >= 2


# ===========================
# Test 9-11: Relationships
# ===========================

def test_create_builds_on_relationship(test_mesh, sample_agents):
    """Test 9: Create BUILDS_ON relationship"""
    # Create two insights
    insight1 = test_mesh.publish_insight("test_sales_001", "Customer inquiry", ["laptop"], confidence=1.0)
    insight2 = test_mesh.publish_insight("test_marketing_001", "Campaign based on inquiry", ["campaign"], confidence=1.0)

    # Create BUILDS_ON relationship
    test_mesh.add_relationship(insight2, insight1, RelationType.BUILDS_ON)

    # Verify relationship
    relationships = test_mesh.get_insight_relationships(insight2, direction="outgoing")
    builds_on = [r for r in relationships if r['relation_type'] == 'BUILDS_ON']
    assert len(builds_on) == 1
    assert builds_on[0]['target_id'] == insight1


def test_create_led_to_relationship(test_mesh, sample_agents):
    """Test 10: Create LED_TO relationship"""
    # Create insights
    insight1 = test_mesh.publish_insight("test_sales_001", "5 inquiries", ["inquiry"], confidence=1.0)
    insight2 = test_mesh.publish_insight("test_inventory_001", "Order 50 laptops", ["order"], confidence=1.0)

    # Create LED_TO relationship (insight1 LED_TO insight2)
    test_mesh.add_relationship(insight1, insight2, RelationType.LED_TO)

    # Verify
    relationships = test_mesh.get_insight_relationships(insight1, direction="outgoing")
    led_to = [r for r in relationships if r['relation_type'] == 'LED_TO']
    assert len(led_to) == 1
    assert led_to[0]['target_id'] == insight2


def test_agent_influence_metrics(test_mesh, sample_agents):
    """Test 11: Get agent influence metrics"""
    # Sales publishes insight
    sales_insight = test_mesh.publish_insight("test_sales_001", "Customer inquiry", ["laptop"], confidence=1.0)

    # Marketing builds on it
    marketing_insight = test_mesh.publish_insight("test_marketing_001", "Campaign", ["campaign"], confidence=1.0)
    test_mesh.add_relationship(marketing_insight, sales_insight, RelationType.BUILDS_ON)

    # Get influence metrics
    influence = test_mesh.get_agent_influence("test_sales_001")

    assert influence['agent_id'] == "test_sales_001"
    assert influence['insights_published'] >= 1
    assert influence['builds_on_count'] >= 1
    assert influence['influenced_count'] >= 1


# ===========================
# Test 12-14: Agent Adapters
# ===========================

def test_adapter_auto_registration(test_mesh):
    """Test 12: Adapter auto-registers agent"""
    adapter = AgentMeshAdapter(
        agent_id="test_adapter_001",
        mesh=test_mesh,
        framework="langchain",
        role="sales"
    )

    # Verify agent was registered
    assert test_mesh.pg_store.agent_exists("test_adapter_001")

    pg_agent = test_mesh.pg_store.get_agent("test_adapter_001")
    assert pg_agent['framework'] == "langchain"
    assert pg_agent['role'] == "sales"


def test_adapter_publish_insight(test_mesh):
    """Test 13: Adapter publishes insight with context"""
    adapter = AgentMeshAdapter("test_adapter_002", test_mesh, "mock", "sales")

    insight_id = adapter.publish_insight(
        observation="Customer wants bulk pricing",
        tags=["pricing", "bulk"],
        context={"product": "laptop", "quantity": 50}
    )

    # Verify insight
    insight = test_mesh.store.get_node(insight_id)
    assert insight['observation'] == "Customer wants bulk pricing"
    assert insight['context']['product'] == "laptop"


def test_adapter_query_operations(test_mesh):
    """Test 14: Adapter query operations with permissions"""
    # Create adapters
    sales = AgentMeshAdapter("test_sales_adapter", test_mesh, "mock", "sales")
    marketing = AgentMeshAdapter("test_marketing_adapter", test_mesh, "mock", "marketing")

    # Sales publishes
    sales.publish_insight("Sales insight", ["sales"])

    # Marketing publishes
    marketing.publish_insight("Marketing insight", ["marketing"])

    # Sales queries (can only see own insights)
    sales_results = sales.query_by_tags(["sales", "marketing"], match_all=False)
    sales_insights = [r for r in sales_results if r['agent_id'] == "test_sales_adapter"]
    assert len(sales_insights) >= 1

    # Marketing queries (can see sales + marketing)
    marketing_results = marketing.query_by_tags(["sales", "marketing"], match_all=False)
    assert len(marketing_results) >= 2  # Both insights visible


# ===========================
# Test 15-17: Decorator-Based Publishing
# ===========================

class MockAgent:
    """Mock agent for testing decorator"""
    def __init__(self, adapter):
        self.adapter = adapter

    @publish_to_mesh(
        observation="{count} customers inquired about {product}",
        tags=["inquiry", "{product}"],
        insight_type="observation",
        context=["product", "count"]
    )
    def log_inquiry(self, product, count):
        return {"product": product, "count": count}

    @publish_to_mesh(
        observation="Campaign created for {product}",
        tags=["{tags}"],  # List expansion
        insight_type="decision",
        builds_on="related_insights"
    )
    def create_campaign(self, product, tags, related_insights=None):
        return {"campaign": f"{product} campaign"}


def test_decorator_template_substitution(test_mesh):
    """Test 15: Decorator template substitution"""
    adapter = AgentMeshAdapter("test_decorator_001", test_mesh, "mock", "sales")
    agent = MockAgent(adapter)

    insight_id = agent.log_inquiry(product="laptop", count=5)

    # Verify insight
    insight = test_mesh.store.get_node(insight_id)
    assert insight['observation'] == "5 customers inquired about laptop"
    assert "laptop" in insight['tags']
    assert insight['context']['product'] == "laptop"
    assert insight['context']['count'] == 5


def test_decorator_list_expansion(test_mesh):
    """Test 16: Decorator list expansion in tags"""
    adapter = AgentMeshAdapter("test_decorator_002", test_mesh, "mock", "marketing")
    agent = MockAgent(adapter)

    insight_id = agent.create_campaign(
        product="laptop",
        tags=["campaign", "laptop", "promotion"]
    )

    # Verify tags expanded
    insight = test_mesh.store.get_node(insight_id)
    assert "campaign" in insight['tags']
    assert "laptop" in insight['tags']
    assert "promotion" in insight['tags']


def test_decorator_auto_relationships(test_mesh):
    """Test 17: Decorator auto-creates relationships"""
    adapter = AgentMeshAdapter("test_decorator_003", test_mesh, "mock", "marketing")
    agent = MockAgent(adapter)

    # Create base insight
    base_insight = test_mesh.publish_insight(
        "test_decorator_003",
        "Sales data",
        ["sales"],
        confidence=1.0
    )

    # Create campaign that builds on base insight
    campaign_insight = agent.create_campaign(
        product="laptop",
        tags=["campaign"],
        related_insights=[base_insight]
    )

    # Verify BUILDS_ON relationship
    relationships = test_mesh.get_insight_relationships(campaign_insight, direction="outgoing")
    builds_on = [r for r in relationships if r['relation_type'] == 'BUILDS_ON']
    assert len(builds_on) == 1
    assert builds_on[0]['target_id'] == base_insight


# ===========================
# Test 18-20: PostgreSQL Integration
# ===========================

def test_postgresql_role_management(test_mesh):
    """Test 18: PostgreSQL role permissions"""
    # Get sales role
    sales_role = test_mesh.pg_store.get_role("sales")
    assert sales_role['role_name'] == "sales"
    assert 'sales' in sales_role['can_access_roles']

    # Get marketing role
    marketing_role = test_mesh.pg_store.get_role("marketing")
    assert 'marketing' in marketing_role['can_access_roles']
    assert 'sales' in marketing_role['can_access_roles']  # Can access sales

    # Get executive role
    executive_role = test_mesh.pg_store.get_role("executive")
    assert len(executive_role['can_access_roles']) >= 5  # Can access many roles


def test_postgresql_audit_logging(test_mesh, sample_agents):
    """Test 19: PostgreSQL audit logging"""
    # Perform actions
    test_mesh.publish_insight(
        "test_sales_001",
        "Test insight",
        ["test"],
        confidence=1.0
    )

    # Query (with audit)
    test_mesh.query_by_tags(
        ["test"],
        requester_role="sales",
        requester_agent_id="test_sales_001"
    )

    # Verify audit logs exist
    logs = test_mesh.pg_store.get_agent_audit_logs("test_sales_001", limit=10)
    assert len(logs) >= 2

    # Check log types
    actions = [log['action'] for log in logs]
    assert 'insight_published' in actions
    assert 'query_by_tags' in actions


def test_mesh_statistics(test_mesh, sample_agents):
    """Test 20: Mesh statistics"""
    # Publish some insights
    test_mesh.publish_insight("test_sales_001", "Insight 1", ["tag1"], confidence=1.0)
    test_mesh.publish_insight("test_sales_001", "Insight 2", ["tag2"], confidence=1.0)
    test_mesh.publish_insight("test_marketing_001", "Insight 3", ["tag3"], confidence=1.0)

    # Get stats
    stats = test_mesh.get_stats()

    assert stats['total_nodes'] >= 7  # 4 agents + 3 insights
    assert stats['total_edges'] >= 3  # At least 3 CREATED relationships
    assert stats['agents'] >= 4
    assert stats['insights'] >= 3


# ===========================
# Test Suite Info
# ===========================

if __name__ == "__main__":
    print("""
    AgentMesh Comprehensive Test Suite
    ==================================

    Test Coverage:
    - Tests 1-4:   Data Models Validation
    - Tests 5-8:   Core Mesh Operations
    - Tests 9-11:  Relationships (BUILDS_ON, LED_TO, Influence)
    - Tests 12-14: Agent Adapters
    - Tests 15-17: Decorator-Based Publishing
    - Tests 18-20: PostgreSQL Integration

    Total: 20 Tests

    Requirements:
    - PostgreSQL database 'agentmesh_test' must exist
    - Run: createdb agentmesh_test

    Run tests:
    pytest tests/test_comprehensive.py -v
    pytest tests/test_comprehensive.py -v --tb=short  # Short traceback
    pytest tests/test_comprehensive.py -k "test_decorator"  # Run specific tests
    """)
