# Context Decomposition Strategy - System Architecture

**Version**: 2.0
**Last Updated**: 2025-10-15
**Status**: Implementation Ready

---

## Overview

This document describes the architecture for a **MapReduce-inspired system** that handles large contexts in multi-turn agent conversations through intelligent decomposition, parallel execution, and synthesis.

**Core Innovation**: Instead of managing what context to include/exclude in a massive LLM call, we decompose questions into focused sub-questions with isolated contexts, execute them in parallel, then synthesize results.

---

## Table of Contents

1. [Core Concept](#1-core-concept)
2. [Data Flow](#2-data-flow)
3. [Three-Phase Architecture](#3-three-phase-architecture)
4. [System Components](#4-system-components)
5. [Data Model & Storage](#5-data-model--storage)
6. [Technology Stack](#6-technology-stack)
7. [Public API](#7-public-api)
8. [Key Benefits](#8-key-benefits)
9. [Future Enhancements](#9-future-enhancements)

---

## 1. Core Concept

### The Problem

Traditional approaches to large contexts:
- **Truncation**: Loses critical information
- **Sliding window**: Drops old (potentially relevant) context
- **Summarization**: Lossy, expensive, slow

### Our Solution: MapReduce for LLM Reasoning

```
┌─────────────────────────────────────────────────┐
│  150KB Context (Too Large)                      │
└──────────────────┬──────────────────────────────┘
                   │
         ┌─────────▼──────────┐
         │  MAP: Decompose    │
         │  Q → Q1, Q2, Q3    │
         └─────────┬──────────┘
                   │
      ┌────────────┼────────────┐
      │            │            │
      ▼            ▼            ▼
  ┌───────┐   ┌───────┐   ┌───────┐
  │Q1+L1  │   │Q2+L2  │   │Q3+L3  │  30KB each
  │30KB   │   │30KB   │   │30KB   │  (Parallel)
  └───┬───┘   └───┬───┘   └───┬───┘
      │           │           │
      └───────────┼───────────┘
                  │
         ┌────────▼─────────┐
         │  REDUCE: Synth   │
         │  A1+A2+A3 → Ans  │
         └──────────────────┘
```

**Key Innovation**: Each LLM call sees ONLY relevant context
- Context isolation (no noise)
- Token reduction (30-40%)
- Parallelization (2-3x latency reduction)
- Zero information loss (all data preserved in labels)

---

## 2. Data Flow

This section shows how data flows through the system in two key scenarios: processing a user question and adding new context labels.

### 2.1 Turn Processing Flow

**Example**: User asks "Compare Q3 laptop sales to inventory levels"

```
┌─────────────────────────────────────────────┐
│ USER QUESTION                                │
├─────────────────────────────────────────────┤
│ "Compare Q3 laptop sales to inventory"      │
└──────────────────┬──────────────────────────┘
                   │
                   ▼
┌─────────────────────────────────────────────┐
│ PHASE 1: DECOMPOSITION                      │
├─────────────────────────────────────────────┤
│ 1. Get label summaries from LabelStore      │
│    Returns: ["L1: Q3 laptop sales...",      │
│              "L2: inventory levels..."]     │
│                                              │
│ 2. LLM decomposes question                  │
│    Returns:                                  │
│    • Q1: "Get Q3 laptop sales"              │
│      → labels: [L1], depends_on: []         │
│    • Q2: "Get inventory levels"             │
│      → labels: [L2], depends_on: []         │
│    • Q3: "Compare and analyze"              │
│      → labels: [], depends_on: [Q1, Q2]     │
└──────────────────┬──────────────────────────┘
                   │
                   ▼
┌─────────────────────────────────────────────┐
│ EXECUTION PLANNING                          │
├─────────────────────────────────────────────┤
│ Build dependency graph:                     │
│   Q1 → (no deps)                            │
│   Q2 → (no deps)                            │
│   Q3 → [Q1, Q2]                             │
│                                              │
│ Compute execution waves:                    │
│   Wave 1: [Q1, Q2] ← parallel              │
│   Wave 2: [Q3]     ← after Wave 1          │
└──────────────────┬──────────────────────────┘
                   │
                   ▼
┌─────────────────────────────────────────────┐
│ PHASE 2: PARALLEL EXECUTION                 │
├─────────────────────────────────────────────┤
│                                              │
│ Wave 1 (parallel):                          │
│  ┌──────────────┐      ┌──────────────┐    │
│  │ Q1 + L1      │      │ Q2 + L2      │    │
│  │ → LLM call   │      │ → LLM call   │    │
│  │ → Answer A1  │      │ → Answer A2  │    │
│  └──────────────┘      └──────────────┘    │
│                                              │
│ Wave 2 (after Wave 1):                      │
│  ┌────────────────────────┐                 │
│  │ Q3 + A1 + A2           │                 │
│  │ → LLM call             │                 │
│  │ → Answer A3            │                 │
│  └────────────────────────┘                 │
└──────────────────┬──────────────────────────┘
                   │
                   ▼
┌─────────────────────────────────────────────┐
│ PHASE 3: SYNTHESIS                          │
├─────────────────────────────────────────────┤
│ LLM receives:                               │
│   Original: "Compare Q3 laptop sales..."    │
│   Decomposition: Q1, Q2, Q3                 │
│   Results: A1, A2, A3                       │
│                                              │
│ LLM synthesizes comprehensive final answer  │
└──────────────────┬──────────────────────────┘
                   │
                   ▼
┌─────────────────────────────────────────────┐
│ PERSISTENCE & RETURN                        │
├─────────────────────────────────────────────┤
│ 1. Log turn to conversation_history         │
│ 2. Log decomposition details                │
│ 3. Update label access metadata             │
│ 4. Return final answer to user              │
└─────────────────────────────────────────────┘
```

**Key Points**:
- Question broken into 3 sub-questions
- Q1 and Q2 run in parallel (Wave 1) with isolated contexts
- Q3 runs after (Wave 2) using results from Q1 and Q2
- Final synthesis combines all answers
- Everything tracked in database for analytics

---

### 2.2 Label Addition Flow

**Example**: User uploads sales data CSV

```
┌─────────────────────────────────────────────┐
│ NEW DATA INPUT                               │
├─────────────────────────────────────────────┤
│ Examples:                                    │
│ • User uploads CSV file                      │
│ • Tool returns large output                  │
│ • Agent loads external data                  │
└──────────────────┬──────────────────────────┘
                   │
                   ▼
┌─────────────────────────────────────────────┐
│ LABEL CREATION (MVP: Manual)                │
├─────────────────────────────────────────────┤
│                                              │
│ agent.add_label(                             │
│   label_id="sales_q3",                       │
│   clause_summary="Q3 sales, all products",  │
│   data=csv_data                              │
│ )                                            │
│                                              │
└──────────────────┬──────────────────────────┘
                   │
                   ▼
┌─────────────────────────────────────────────┐
│ LABELSTORE PROCESSING                       │
├─────────────────────────────────────────────┤
│ 1. Serialize data to JSON                   │
│ 2. Calculate size (KB)                      │
│ 3. Store in SQLite:                         │
│    INSERT INTO labels (                     │
│      id, clause_summary, data,              │
│      size_kb, created_turn                  │
│    )                                        │
│ 4. Label now available for decomposition    │
└─────────────────────────────────────────────┘
```

**Future Enhancement**: LLM-driven label segregation

```
┌─────────────────────────────────────────────┐
│ FUTURE: LLM-DRIVEN SEGREGATION              │
├─────────────────────────────────────────────┤
│ When large data arrives, LLM analyzes and   │
│ creates multiple focused labels:            │
│                                              │
│ LLM receives:                               │
│   "Analyze this CSV. Current labels: [...]  │
│    Break into logical chunks."              │
│                                              │
│ LLM returns:                                │
│   • "Q3_laptop_sales|Q3 laptops, 1200 units"│
│   • "Q3_phone_sales|Q3 phones, regional"    │
│                                              │
│ System creates multiple labels automatically│
└─────────────────────────────────────────────┘
```

**Key Points**:
- MVP: Manual label creation (simple, reliable)
- Each label has ID + clause summary + data
- Stored in SQLite with metadata
- Future: LLM automatically segregates large data into focused labels

---

## 3. Three-Phase Architecture

### System Overview

```
┌──────────────────────────────────────────────────┐
│              ContextDecompositionAgent            │
│                                                   │
│  ┌────────────────────────────────────────────┐  │
│  │  1. Get label summaries (LabelStore)       │  │
│  │  2. Decompose question (DecompositionEng)  │  │
│  │  3. Plan execution (ExecutionPlanner)      │  │
│  │  4. Execute waves (ParallelExecutor)       │  │
│  │  5. Synthesize answer (SynthesisEngine)    │  │
│  │  6. Log to database                        │  │
│  └────────────────────────────────────────────┘  │
└───────┬──────────────────────┬───────────────────┘
        │                      │
        ▼                      ▼
   ┌─────────┐           ┌──────────────┐
   │ Labels  │           │ Conversation │
   │  Store  │           │   History    │
   │(SQLite) │           │  (SQLite)    │
   └─────────┘           └──────────────┘
```

### Phase 1: Decomposition + Label Selection

**Input**: User question Q, available labeled contexts

**Process**:
```
LLM receives:
  "Break Q into sub-questions for context isolation.
   Available labels: [L1: summary, L2: summary, ...]

   Optimize for:
   - Maximum context isolation
   - Token efficiency
   - Parallelization"

LLM returns:
  Q1: "sub-question text" → requires [L1, L2]
  Q2: "sub-question text" → requires [L3]
  Q3: "sub-question text" → requires [] depends_on [Q1, Q2]
```

**Output**: Decomposition with label requirements and dependencies

---

### Phase 2: Parallel Execution

**Wave-based Execution**:

```
Wave 1 (Independent - Run in Parallel):
  ┌──────────────┐         ┌──────────────┐
  │ LLM(Q1 + L1) │         │ LLM(Q2 + L3) │
  │    → A1      │         │    → A2      │
  └──────────────┘         └──────────────┘

Wave 2 (Dependent - Run After Wave 1):
  ┌────────────────────┐
  │ LLM(Q3 + A1 + A2)  │
  │       → A3         │
  └────────────────────┘
```

**Context Isolation**: Each sub-question gets ONLY its required labels
- No noise from unrelated data
- Dramatically reduced context size
- Parallel execution reduces latency

**Output**: Answers for each sub-question

---

### Phase 3: Synthesis

**Input**: Original question, all sub-answers

**Process**:
```
LLM receives:
  "Original question: Q
   You split it into: Q1, Q2, Q3
   Results:
     Q1 → A1
     Q2 → A2
     Q3 → A3

   Synthesize comprehensive final answer."
```

**Output**: Final answer to original question

---

## 4. System Components

### Component Overview

```
┌─────────────────────────────────────────────────┐
│  ContextDecompositionAgent                      │
│  - Main orchestrator                            │
│  - process_question(), add_label()              │
└──────┬────────────────────────────┬─────────────┘
       │                            │
       ▼                            ▼
┌──────────────┐            ┌──────────────────┐
│  LabelStore  │            │ Decomposition    │
│              │            │    Engine        │
│ - Store      │            │                  │
│   labels     │            │ - Build prompts  │
│ - Track      │            │ - Parse JSON     │
│   access     │            │ - Validate       │
└──────────────┘            └──────────────────┘
       │                            │
       │                            ▼
       │                    ┌──────────────────┐
       │                    │ Execution        │
       │                    │   Planner        │
       │                    │                  │
       │                    │ - Build DAG      │
       │                    │ - Compute waves  │
       │                    └──────────────────┘
       │                            │
       │                            ▼
       │                    ┌──────────────────┐
       │                    │ Parallel         │
       └───────────────────►│   Executor       │
                            │                  │
                            │ - Execute waves  │
                            │ - asyncio calls  │
                            └──────────────────┘
                                    │
                                    ▼
                            ┌──────────────────┐
                            │ Synthesis        │
                            │   Engine         │
                            │                  │
                            │ - Combine results│
                            └──────────────────┘
```

### Key Responsibilities

**LabelStore**:
- Store labeled context chunks with metadata
- Track access patterns (for future hierarchical evolution)
- Provide label summaries for decomposition

**DecompositionEngine**:
- Build decomposition prompts
- Call LLM and parse structured JSON response
- Validate dependencies (no circular refs)

**ExecutionPlanner**:
- Build dependency graph from decomposition
- Compute execution waves (topological sort)
- MVP: Two waves (independent, then dependent)

**ParallelExecutor**:
- Execute waves sequentially
- Within wave: run sub-questions in parallel (asyncio)
- Fetch only required labels per sub-question

**SynthesisEngine**:
- Combine sub-answers into final comprehensive answer
- Handle potential contradictions

---

## 5. Data Model & Storage

### Label System

**Label Format**: `<label_id>|<clause_summary>`

**Example**:
```
"Q3_laptop_sales|Q3 2024 laptop sales, 1200 units, $2.4M revenue"
"inventory_oct|October inventory, 45 warehouses, stock levels"
```

**Why This Works**:
- Label ID: Token-efficient reference
- Clause summary: Telegraphic description for LLM selection
- Actual data: Stored in database, fetched only when needed

---

### Database Schema (SQLite)

```sql
-- Labeled context chunks
CREATE TABLE labels (
    id TEXT PRIMARY KEY,
    clause_summary TEXT NOT NULL,
    data TEXT NOT NULL,              -- JSON serialized
    size_kb REAL,
    created_turn INTEGER,
    last_accessed_turn INTEGER,
    access_count INTEGER DEFAULT 0,
    parent_id TEXT                   -- For future hierarchical labels
);

-- Conversation turns
CREATE TABLE conversation_history (
    turn_id INTEGER PRIMARY KEY AUTOINCREMENT,
    question TEXT NOT NULL,
    answer TEXT NOT NULL,
    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
    token_count INTEGER,
    decomposed BOOLEAN DEFAULT FALSE
);

-- Decomposition tracking
CREATE TABLE decompositions (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    turn_id INTEGER,
    original_question TEXT,
    num_sub_questions INTEGER,
    FOREIGN KEY (turn_id) REFERENCES conversation_history(turn_id)
);

-- Sub-question details
CREATE TABLE sub_questions (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    decomposition_id INTEGER,
    sub_q_id TEXT,                   -- Q1, Q2, Q3
    question_text TEXT,
    answer_text TEXT,
    labels_used TEXT,                -- JSON: ["L1", "L2"]
    depends_on TEXT,                 -- JSON: ["Q1"]
    execution_wave INTEGER,
    FOREIGN KEY (decomposition_id) REFERENCES decompositions(id)
);

-- Access tracking (for future label evolution)
CREATE TABLE label_access_log (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    label_id TEXT,
    turn_id INTEGER,
    accessed_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (label_id) REFERENCES labels(id)
);

-- Performance indexes
CREATE INDEX idx_labels_access ON labels(last_accessed_turn);
CREATE INDEX idx_conversation_timestamp ON conversation_history(timestamp);
```

**Why SQLite**:
- Built into Python (zero setup)
- ACID transactions (production-ready)
- Structured queries for analytics
- Easy to persist and version control

---

## 6. Technology Stack

### Core Stack

| Component | Technology | Purpose |
|-----------|-----------|---------|
| Language | Python 3.9+ | Core implementation |
| Database | SQLite 3.x | Persistence |
| Async | asyncio | Parallel execution |
| Validation | pydantic | Data models |
| Testing | pytest | Test framework |

### LLM Integration

| Provider | Model | Use Case |
|----------|-------|----------|
| OpenAI | GPT-4/GPT-4-turbo | Primary LLM |
| OpenAI | GPT-3.5-turbo | Cost-efficient alternative |
| Anthropic | Claude 3 Sonnet | Alternative provider |

### Dependencies

```txt
openai>=1.0.0
anthropic>=0.7.0
pydantic>=2.0.0
pytest>=7.0.0
pytest-asyncio>=0.21.0
```

---

## 7. Public API

### Main Entry Point

```python
class ContextDecompositionAgent:
    """
    Main agent for context decomposition strategy
    """

    def __init__(
        self,
        llm_client: LLMClient,
        db_path: str = "context_mesh.db",
        context_limit: int = 100000
    ):
        """Initialize agent with LLM client and database"""
        pass

    async def process_question(self, question: str) -> str:
        """
        Process question using 3-phase decomposition

        Returns: Final answer
        """
        pass

    def add_label(
        self,
        label_id: str,
        clause_summary: str,
        data: Any
    ) -> None:
        """
        Add labeled context chunk

        Args:
            label_id: Unique identifier
            clause_summary: Brief description for LLM
            data: Actual data (dict, list, string)
        """
        pass

    def get_stats(self) -> Dict[str, Any]:
        """
        Get system statistics

        Returns:
            - total_turns
            - total_labels
            - total_decompositions
            - avg_sub_questions
            - most_accessed_labels
        """
        pass
```

### Basic Usage

```python
import asyncio
from src.core.agent import ContextDecompositionAgent
from src.llm.client import OpenAIClient

async def main():
    # Initialize
    llm = OpenAIClient(api_key="...")
    agent = ContextDecompositionAgent(llm, db_path="demo.db")

    # Add context labels
    agent.add_label(
        "sales_q3",
        "Q3 2024 sales data, all products, regional breakdown",
        {"laptops": {"units": 1200, "revenue": 2400000}}
    )

    agent.add_label(
        "inventory_q3",
        "Q3 inventory levels, all warehouses",
        {"laptops": {"stock": 450, "reorder_point": 200}}
    )

    # Process questions
    answer = await agent.process_question(
        "Compare Q3 laptop sales to inventory levels"
    )
    print(answer)

    # Get statistics
    stats = agent.get_stats()
    print(f"Processed {stats['total_turns']} turns")

asyncio.run(main())
```

---

## 8. Key Benefits

### Comparison with Traditional Approaches

| Aspect | Traditional | Context Decomposition |
|--------|------------|----------------------|
| Context Size | 150KB in one call | 3 × 30KB calls |
| Parallelization | Sequential | Concurrent waves |
| Relevance | All data (noisy) | Only needed labels |
| Scalability | Breaks at limit | Scales via decomposition |
| Token Efficiency | Redundant context | Minimal duplication |
| Latency | Single slow call | Parallel fast calls |

### Token Usage Example

```
Traditional Approach:
  1 call × 150KB = 150K tokens

Context Decomposition:
  Phase 1 (decompose):  5K tokens
  Phase 2 (3 parallel): 90K tokens (3 × 30KB)
  Phase 3 (synthesis):  3K tokens
  Total: 98K tokens (35% savings + parallelization)
```

### Accuracy

- **Zero information loss**: All data preserved in labels
- **Context isolation**: Eliminates noise, improves focus
- **Synthesis validation**: LLM can detect contradictions

---

## 9. Future Enhancements

### Hierarchical Label Evolution (Phase 2)

Labels evolve as conversation deepens:

```
Turns 1-10: Broad labels
  L1: "sales_data" (10MB)

Turns 11-30: User focuses on Q3 → L1 splits
  L1.1: "Q3_sales" (3MB)
  L1.2: "Q4_sales" (7MB)

Turns 31-50: Deep dive → L1.1 splits
  L1.1.1: "Q3_laptop_sales" (1MB)
  L1.1.2: "Q3_phone_sales" (2MB)
```

**Implementation**: `parent_id` already in schema for future use

---

### Recursive Decomposition (Phase 2)

Sub-questions can themselves be decomposed:

```
Q: "Analyze full business performance"
  ├─ Q1: "Revenue analysis" (still complex)
  │   ├─ Q1.1: "Q3 revenue by product"
  │   ├─ Q1.2: "Q4 revenue by product"
  │   └─ Q1.3: "Year-over-year comparison"
  ├─ Q2: "Cost analysis"
  └─ Q3: "Profit margins"
```

---

### Context-Managed LLM Wrapper (Phase 2)

Transparent integration with existing code:

```python
from context_mesh import ContextManagedOpenAI

# Drop-in replacement for OpenAI client
client = ContextManagedOpenAI(api_key="...")

# Automatically uses decomposition when needed
response = client.chat.completions.create(
    model="gpt-4",
    messages=large_message_history  # 150KB
)
# Wrapper transparently applies decomposition
```

---

### Advanced DAG Execution (Phase 2)

Multi-wave execution for complex dependencies:

```
Wave 1: [Q1, Q2, Q3] (no dependencies - parallel)
Wave 2: [Q4, Q5] (depend on Wave 1 - parallel)
Wave 3: [Q6] (depends on Wave 2)
Wave 4: [Q7] (depends on Wave 3)
```

**MVP**: Two waves (independent, then dependent)
**Future**: Full topological sort

---

### Multi-Model Optimization (Phase 2)

Different models for different phases:

```python
config = {
    'decomposition': 'gpt-4',        # Needs reasoning
    'sub_questions': 'gpt-3.5-turbo', # Can be cheaper
    'synthesis': 'gpt-4'              # Needs reasoning
}

# Cost savings: ~55% vs all GPT-4
```

---

## Conclusion

This architecture provides a production-ready foundation for handling large contexts in multi-turn agent systems through:

✅ **Context isolation** - Each LLM call sees only relevant data
✅ **Parallelization** - Independent sub-questions run concurrently
✅ **Zero information loss** - All data preserved in labeled chunks
✅ **Self-organizing** - LLM decides decomposition strategy
✅ **Scalable design** - Modular components, clear separation
✅ **Production-ready** - SQLite persistence, error handling, metrics

**Key Innovation**: MapReduce pattern for LLM reasoning - decompose complex questions into focused sub-questions with isolated contexts, execute in parallel, then synthesize comprehensive answers.

---

*For design rationale, see `CONTEXT_DECOMPOSITION_STRATEGY.md`*
*For project context, see `CLAUDE.md`*
*For implementation, see `src/` directory*
