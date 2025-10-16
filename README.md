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

## Reasoning & Problem-Solving Process

**AI-assisted development as a core workflow**
Integrated AI Agent throughout the development process—from architectural design discussions to rapid prototyping and documentation. Used it as a thinking partner to explore trade-offs, validate design decisions, and accelerate implementation.

**Deep exploration before commitment**
Evaluated 10+ architectural approaches for Large Context Handling (3-tier storage, event sourcing, graph-based, hierarchical) before selecting MapReduce-inspired decomposition. Each alternative documented with trade-offs. For AgentMesh, compared NetworkX vs Neo4j, tag-based vs RBAC, GraphQL vs REST—chose hybrid PostgreSQL + NetworkX for the right balance of simplicity and production-readiness.

**Developer experience as first-class concern**
Built decorator pattern reducing agent integration from ~20 lines to ~5 lines (80% less boilerplate). Production systems succeed only if adoption is frictionless. If integration is hard, teams won't use it—no matter how powerful the underlying system.

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
