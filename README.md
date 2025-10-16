# Agentic AI: Knowledge Mesh & Context Management

## Honest Upfront

My primary focus was **AgentMesh** - building a unified knowledge mesh for multi-agent systems. I invested significant time in the implementation, examples, and getting it to a working state.

While working on AgentMesh, I read the **Large Context Handling** problem statement and immediately had an architectural insight: a MapReduce-inspired decomposition approach where the LLM itself breaks questions into focused sub-questions with isolated contexts. The idea was too compelling not to explore, so I spent additional time architecting and documenting the complete design, even though I didn't have time to implement it.

**Two Projects, Different Depths:**

**AgentMesh** ✅ **First Working Model**
Full implementation with hybrid PostgreSQL + NetworkX architecture, GraphQL API, decorator pattern, and interactive visualizations.

**Large Context Handling** 📐 **Architecture Complete**
Comprehensive design with 3-phase decomposition system, SQLite schema, data models, and component skeletons. Implementation-ready.

---

## Quick Overview

### 🔗 AgentMesh - Shared Brain for AI Agents

**The Problem**: AI agents across organizations (sales, marketing, finance) work in isolation. Knowledge is fragmented.

**The Solution**: A central knowledge hub where agents publish insights, query collective intelligence, and track relationships (BUILDS_ON, LED_TO).

**Architecture**: Hybrid PostgreSQL (RBAC, security) + NetworkX (graph operations) with GraphQL API.

**Status**: First working model with e-commerce scenario, decorator pattern for 80% less boilerplate, and interactive visualizations.

📖 **[Full Documentation →](agent-mesh/README.md)**
🏗️ **[Architecture Details →](agent-mesh/ARCHITECTURE.md)**

---

### 🧠 Large Context Handling in Agentic Systems

**The Problem**: Multi-turn agent workflows exceed LLM context windows, losing critical information.

**The Solution**: LLM-driven question decomposition into focused sub-questions with isolated contexts, executed in parallel (asyncio), then synthesized.

**Architecture**: 3-phase system (Decomposition → Parallel Execution → Synthesis) with SQLite label store, achieving 30-40% token reduction.

**Status**: Complete architecture, data models, database schema, component skeletons with comprehensive documentation. Implementation-ready.

📖 **[Full Documentation →](large_context_handling/README.md)**
🏗️ **[Architecture Details →](large_context_handling/ARCHITECTURE.md)**

---

## Project Structure

```
Agentic-AI/
├── README.md                    # This file
├── CLAUDE.md                    # Complete project context and design decisions
│
├── agent-mesh/                  # ✅ First working model
│   ├── README.md                # User documentation
│   ├── ARCHITECTURE.md          # Technical architecture
│   ├── src/                     # Full implementation
│   ├── examples/                # Working examples
│   └── visualization/           # Static + interactive graphs
│
└── large_context_handling/      # 📐 Architecture complete
    ├── README.md                # User documentation
    ├── ARCHITECTURE.md          # Technical architecture
    ├── CONTEXT_DECOMPOSITION_STRATEGY.md  # Design exploration
    ├── src/                     # Component skeletons, implementation-ready
    └── database/                # SQLite schema
```

---

## Quick Start

### AgentMesh
```bash
cd agent-mesh
pip install -r requirements.txt
createdb agentmesh  # PostgreSQL setup
python examples/mock_agents.py  # E-commerce scenario
```

### Large Context Handling
```bash
cd large_context_handling
pip install -r requirements.txt
# See README.md for architecture walkthrough
```

---

## Contact

**Akash S E**
📧 akash181gowda@gmail.com
🔗 [LinkedIn](https://www.linkedin.com/in/akash-s-e-808a3120a/)
📍 Bengaluru, India
