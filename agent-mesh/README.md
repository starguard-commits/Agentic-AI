# AgentMesh

**A unified knowledge mesh for multi-agent systems**

AgentMesh enable AI agents to share insights and achieve collective intelligence across your organization. Think of it as "Slack for AI agents" - a central hub where agents publish what they learn and query what others have discovered.

---

## The Problem

Your organization has multiple AI agents working in isolation:
- Sales agent learns "customers want feature X" but Engineering never hears it
- Marketing discovers "campaign Y works" but Sales doesn't leverage it
- Each agent reinvents the wheel instead of building on collective knowledge

**Result**: Siloed insights, missed opportunities, duplicated effort.

---

## The Solution

AgentMesh creates a shared knowledge graph where:
- ✅ Agents publish insights with one line of code
- ✅ Agents query collective knowledge across the org
- ✅ Relationships track how insights influence each other
- ✅ Role-based permissions keep data secure

**Result**: Collective intelligence, better decisions, organizational learning.

---

## Quick Start

### Installation

Install from Package (Recommended)**

```bash
# Install from source distribution
pip install agentmesh-1.0.0.tar.gz

# Or install from wheel
pip install agentmesh-1.0.0-py3-none-any.whl

# Setup PostgreSQL (one-time)
createdb agentmesh
```

**Option 2: Install from Source (Development)**

```bash
# Clone repository
git clone <repository-url>
cd agentmesh

# Install in development mode (editable)
pip install -e .

# Or install with optional dependencies
pip install -e ".[dev,viz,api]"

# Setup PostgreSQL (one-time)
createdb agentmesh
```

**Option 3: Build Distribution**

```bash
# Clone repository
git clone <repository-url>
cd agentmesh

# Build distribution packages
python setup.py sdist bdist_wheel

# This creates:
# - dist/agentmesh-1.0.0.tar.gz (source distribution)
# - dist/agentmesh-1.0.0-py3-none-any.whl (wheel)

# Install the built package
pip install dist/agentmesh-1.0.0.tar.gz
```

### Basic Usage

```python
from agentmesh.core.mesh import AgentMesh
from agentmesh.adapters import AgentMeshAdapter
from agentmesh.decorators import publish_to_mesh

# Initialize mesh
mesh = AgentMesh(
    persist_path="agentmesh.pkl",
    pg_config={
        'host': 'localhost',
        'database': 'agentmesh',
        'user': 'postgres',
        'password': 'postgres'
    }
)

# Create agent with adapter
class SalesAgent:
    def __init__(self, agent_id, mesh):
        self.adapter = AgentMeshAdapter(agent_id, mesh, "custom", "sales")

    # Use decorator for zero-boilerplate publishing
    @publish_to_mesh(
        observation="{count} customers inquired about {product}",
        tags=["inquiry", "{product}"]
    )
    def log_inquiry(self, product, count):
        pass  # Decorator handles everything!

# Use it
agent = SalesAgent("sales_001", mesh)
agent.log_inquiry("laptop", 5)  # Auto-published to mesh!

# Query collective knowledge
insights = mesh.query_by_tags(["laptop"], requester_role="sales")
print(f"Found {len(insights)} insights about laptops")
```

---

## Key Features

### 1. Zero-Boilerplate Integration
Use the `@publish_to_mesh` decorator to eliminate manual publishing code:

```python
@publish_to_mesh(
    observation="Campaign {name} converted {rate}%",
    tags=["campaign", "{name}"],
    builds_on="sales_insights"  # Auto-creates relationships!
)
def track_campaign(self, name, rate, sales_insights):
    pass
```

### 2. Automatic Relationships
Track how insights influence each other:
- **CREATED**: Who created what (automatic)
- **BUILDS_ON**: This insight references another
- **LED_TO**: This insight caused another

### 3. Role-Based Permissions
Control who sees what:
- Sales sees only sales insights
- Marketing sees marketing + sales
- Executives see everything

### 4. Hybrid Storage
- **PostgreSQL**: Agents, roles, permissions, audit logs
- **NetworkX**: Insights, relationships (upgradeable to Neo4j)

---

## Examples

### E-Commerce Scenario

After installing AgentMesh, see the `examples/` directory for complete demos:

```
Day 1: Sales logs "5 customers want bulk laptop pricing"
Day 2: Marketing creates "Laptop Sale" campaign (builds on sales insight)
Day 3: Inventory orders 50 laptops (led to by sales + marketing)

Result: Collective intelligence → Better decisions
```

**Note**: Examples are located **outside** the package in the repository. After installing AgentMesh, download examples separately from the git repository.

### Available Examples

```bash
# Download agent_usage_examples from repository
git clone <repository-url>
cd agent_usage_examples/

# Run agent_usage_examples (requires AgentMesh to be installed)
python basic_usage.py       # Basic usage walkthrough
python mock_agents.py        # E-commerce scenario with decorators
python graphql_queries.py    # GraphQL API agent_usage_examples
```

**See `examples/README.md` for detailed instructions and troubleshooting.**

---

## Architecture

AgentMesh uses a **hybrid architecture**:
- **PostgreSQL** for security-critical data (agents, roles, audit)
- **NetworkX** for knowledge graph (insights, relationships)
- **Decorator layer** for zero-boilerplate integration
- **GraphQL API** for flexible queries (optional)

**For detailed architecture**, see [ARCHITECTURE.md](ARCHITECTURE.md)

**For relationship types**, see [RELATIONSHIPS.md](RELATIONSHIPS.md)

---

## Requirements

- Python 3.8+
- PostgreSQL 12+
- Dependencies: networkx, graphene, psycopg2-binary (see `requirements.txt`)

---

## Project Structure

```
project/
├── agentmesh/               # Main package (pip installable)
│   ├── src/
│   │   ├── core/            # Mesh core, graph storage, PostgreSQL
│   │   ├── adapters/        # Agent adapters (auto-registration)
│   │   ├── decorators/      # @publish_to_mesh decorator
│   │   ├── api/             # GraphQL API (optional)
│   │   └── models/          # Data models
│   ├── tests/               # Tests
│   ├── setup.py             # Package configuration
│   ├── build.sh             # Build script
│   └── README.md            # This file
│
└── examples/                # Usage examples (separate from package)
    ├── basic_usage.py       # Basic operations
    ├── mock_agents.py       # E-commerce scenario
    ├── graphql_queries.py   # GraphQL examples
    └── README.md            # Example instructions
```

**Note**: After installing the package, examples need to be downloaded separately from the repository.

---

## Usage Patterns

### Pattern 1: Decorator (Recommended)

```python
@publish_to_mesh(
    observation="{count} users signed up",
    tags=["signup", "{source}"]
)
def track_signup(self, count, source):
    pass
```

### Pattern 2: Direct Publishing

```python
self.adapter.publish_insight(
    observation="User signed up",
    tags=["signup", "email"],
    context={"user_id": 123}
)
```

### Pattern 3: With Relationships

```python
@publish_to_mesh(
    observation="Launched {campaign}",
    tags=["campaign"],
    builds_on="analysis_insights"
)
def launch_campaign(self, campaign, analysis_insights):
    pass
```

---

## Documentation

- **[README.md](README.md)** - This file (getting started)
- **[ARCHITECTURE.md](ARCHITECTURE.md)** - Detailed architecture, next steps
- **[RELATIONSHIPS.md](RELATIONSHIPS.md)** - Relationship types explained
- **[CLAUDE.md](CLAUDE.md)** - Project context, implementation history

---

## Production Deployment

**Current**: MVP/Prototype with NetworkX + PostgreSQL
- Good for: 1000s of insights, 10s of agents
- Deployment: Single process

**Next Steps**: See [ARCHITECTURE.md - Next Steps to Harden Architecture](ARCHITECTURE.md#next-steps-to-harden-architecture)
- Neo4j migration for scale
- Authentication (API keys, JWT)
- Monitoring & observability
- Multi-tenancy

---

## FAQ

**Q: Do I need to setup Neo4j?**
A: No, AgentMesh uses NetworkX by default. Neo4j is for production scale.

**Q: Is PostgreSQL required?**
A: Yes, for agents, roles, and audit logs. Setup is automatic - just `createdb agentmesh`.

**Q: Can I use this with LangChain/CrewAI?**
A: Yes! Use `AgentMeshAdapter` to wrap any agent framework.

**Q: How do permissions work?**
A: Role-based. Each agent has a role (sales, marketing, etc). Roles define what they can see. Permissions are enforced at query time.

**Q: Can agents from different frameworks share knowledge?**
A: Yes! That's the whole point. LangChain, CrewAI, OpenAI, custom agents - all work together.

---

## Building and Distribution

### Building Packages

AgentMesh can be packaged for distribution using standard Python packaging tools:

```bash
# Install build tools (one-time)
pip install build wheel setuptools

# Build both source distribution (.tar.gz)
python setup.py sdist

# Output files created in dist/:
# - agentmesh-1.0.0.tar.gz       (source distribution)
# - agentmesh-1.0.0-py3-none-any.whl  (wheel - faster install)
```

### Installing Built Package

```bash
# Install source distribution
pip install dist/agentmesh-1.0.0.tar.gz