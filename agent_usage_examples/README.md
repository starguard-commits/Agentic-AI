# AgentMesh Examples

This directory contains example scripts demonstrating how to use AgentMesh after installation.

---

## Prerequisites

### 1. Install AgentMesh Package

```bash
# Install from built distribution
pip install agentmesh-1.0.0.tar.gz

# Or install from wheel (faster)
pip install agentmesh-1.0.0-py3-none-any.whl

# Or install from source (development)
cd ../agentmesh
pip install -e .
```

### 2. Setup PostgreSQL Database

```bash
# Create database (one-time)
createdb agentmesh

# Verify database exists
psql -l | grep agentmesh
```

### 3. Verify Installation

```python
# Test import
python -c "from agentmesh.core.mesh import AgentMesh; print('✓ AgentMesh installed!')"
```

---

## Examples

### 1. basic_usage.py

**Purpose**: Demonstrates fundamental AgentMesh operations

**What it shows**:
- Creating a mesh with PostgreSQL connection
- Registering agents with adapters
- Publishing insights
- Creating relationships between insights
- Querying insights (by tags, by agent, by time)
- Checking agent influence
- Using GraphQL API
- Saving mesh to disk

**Run**:
```bash
python basic_usage.py
```

**Expected output**:
- Creates 2 agents (sales, marketing)
- Publishes 3 insights
- Creates 1 relationship (BUILDS_ON)
- Queries insights by tags and agent
- Shows agent influence metrics
- Saves mesh to `demo_mesh.pkl`

---

### 2. mock_agents.py

**Purpose**: Realistic e-commerce scenario with 3 agents using decorators

**What it shows**:
- **Decorator-based integration** (`@publish_to_mesh`)
- Sales agent logs customer inquiries
- Marketing agent creates campaigns based on sales insights
- Inventory agent adjusts stock based on demand
- Automatic relationship creation (BUILDS_ON, LED_TO)
- Cross-agent knowledge sharing
- Agent influence metrics

**Run**:
```bash
python mock_agents.py
```

**Scenario Flow**:
```
Day 1: Sales logs customer inquiries
  → 5 customers want bulk laptop pricing
  → 3 customers want gaming specs
  → Sales trend: high-performance laptops in demand

Day 2: Marketing analyzes trends
  → Finds sales insights about laptops
  → Creates "Laptop Mega Sale" campaign
  → Campaign BUILDS_ON sales insights

Day 3: Inventory adjusts stock
  → Finds sales + marketing insights
  → Decides to order 50 more laptops
  → Decision LED_TO by sales + marketing
```

**Expected output**:
- 3 agents created (sales, marketing, inventory)
- 5 insights published
- 2 relationship types used (BUILDS_ON, LED_TO)
- Influence metrics for each agent
- Mesh statistics
- Saves mesh to `ecommerce_mesh.pkl`

---

### 3. graphql_queries.py

**Purpose**: Demonstrates GraphQL query interface

**What it shows**:
- Various GraphQL queries against the mesh
- Query all agents
- Query insights by tags
- Query insights by agent
- Get agent influence
- Get mesh statistics
- Get topics
- Complex queries with match conditions

**Run**:
```bash
python graphql_queries.py
```

**Expected output**:
- 7 different GraphQL queries executed
- JSON-formatted results for each query
- Examples of simple and complex queries
- Permission-aware queries (role-based)
- Saves mesh to `graphql_demo.pkl`

---

## Common PostgreSQL Configuration

All examples use this PostgreSQL configuration by default:

```python
pg_config = {
    'host': 'localhost',
    'port': 5432,
    'database': 'agentmesh',
    'user': 'postgres',
    'password': 'postgres'
}
```

**To customize**:

Edit the `pg_config` dictionary in each example, or set environment variables:

```bash
export AGENTMESH_DB_HOST=localhost
export AGENTMESH_DB_PORT=5432
export AGENTMESH_DB_NAME=agentmesh
export AGENTMESH_DB_USER=your_user
export AGENTMESH_DB_PASSWORD=your_password
```

Then update examples to read from environment:

```python
import os

pg_config = {
    'host': os.getenv('AGENTMESH_DB_HOST', 'localhost'),
    'port': int(os.getenv('AGENTMESH_DB_PORT', 5432)),
    'database': os.getenv('AGENTMESH_DB_NAME', 'agentmesh'),
    'user': os.getenv('AGENTMESH_DB_USER', 'postgres'),
    'password': os.getenv('AGENTMESH_DB_PASSWORD', 'postgres')
}
```

---

## Troubleshooting

### Error: "No module named 'agentmesh'"

**Cause**: Package not installed

**Fix**:
```bash
# Check if installed
pip show agentmesh

# If not, install it
pip install agentmesh-1.0.0.tar.gz
```

### Error: "could not connect to server: Connection refused"

**Cause**: PostgreSQL not running

**Fix**:
```bash
# Start PostgreSQL (macOS with Homebrew)
brew services start postgresql

# Or manually
pg_ctl -D /usr/local/var/postgres start

# Verify it's running
psql -U postgres -c "SELECT version();"
```

### Error: "database 'agentmesh' does not exist"

**Cause**: Database not created

**Fix**:
```bash
# Create database
createdb agentmesh

# Or via psql
psql -U postgres -c "CREATE DATABASE agentmesh;"
```

### Error: "password authentication failed"

**Cause**: Incorrect PostgreSQL credentials

**Fix**:
1. Update `pg_config` in examples with correct credentials
2. Or change PostgreSQL authentication settings in `pg_hba.conf`

---

## Next Steps

After running these examples:

1. **Build your own agents**: Use the decorator pattern from `mock_agents.py`
2. **Integrate with existing agents**: Wrap LangChain/CrewAI agents with `AgentMeshAdapter`
3. **Explore GraphQL**: Use `graphql_queries.py` as reference for querying
4. **Deploy to production**: See `../agentmesh/ARCHITECTURE.md` for FastAPI deployment

---

## Additional Resources

- **README.md**: Package overview and quick start
- **ARCHITECTURE.md**: Detailed architecture and deployment models
- **RELATIONSHIPS.md**: Explanation of relationship types
- **PACKAGING.md**: Building and distributing the package
- **FASTAPI_PLAN.md**: Production deployment as microservice

---

*Last updated: 2025-10-13*
