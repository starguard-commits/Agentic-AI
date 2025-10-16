"""
Basic Demo - Context Decomposition Strategy

Demonstrates the 3-phase decomposition approach with a simple example.

TODO: This demo is not yet functional - it shows the intended usage pattern.
      Complete the core components to make this work.
"""

import asyncio
import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.core.agent import ContextDecompositionAgent
from src.llm.client import create_llm_client
from config import Config


async def main():
    """
    Basic demo showing agent usage.

    Steps:
    1. Initialize agent
    2. Add labels with context data
    3. Ask questions
    4. View results and metrics
    """

    print("=" * 60)
    print("Context Decomposition Strategy - Basic Demo")
    print("=" * 60)

    # Step 1: Initialize agent
    print("\n[1] Initializing agent...")

    # TODO: Set your API key in environment or here
    # export OPENAI_API_KEY="sk-..."

    llm_client = create_llm_client(
        provider="openai",
        api_key=Config.OPENAI_API_KEY,
        model="gpt-4"
    )

    agent = ContextDecompositionAgent(
        llm_client=llm_client,
        db_path="demo.db",
        context_limit=100000
    )

    print("✓ Agent initialized")

    # Step 2: Add labels (context data)
    print("\n[2] Adding labels...")

    # Label 1: Sales data
    sales_data = {
        "Q3_2024": {
            "laptops": {
                "units_sold": 1200,
                "revenue": 2400000,
                "regions": {
                    "north": 450,
                    "south": 380,
                    "east": 220,
                    "west": 150
                }
            },
            "phones": {
                "units_sold": 3500,
                "revenue": 1750000,
                "regions": {
                    "north": 1200,
                    "south": 980,
                    "east": 800,
                    "west": 520
                }
            }
        }
    }

    agent.add_label(
        label_id="sales_q3",
        clause_summary="Q3 2024 sales data, laptops and phones, regional breakdown",
        data=sales_data
    )

    # Label 2: Inventory data
    inventory_data = {
        "current_stock": {
            "laptops": 450,
            "phones": 890
        },
        "reorder_points": {
            "laptops": 200,
            "phones": 500
        },
        "warehouses": ["WH-North", "WH-South", "WH-East"]
    }

    agent.add_label(
        label_id="inventory_q3",
        clause_summary="Q3 inventory levels, stock and reorder points",
        data=inventory_data
    )

    print("✓ Added 2 labels: sales_q3, inventory_q3")

    # Step 3: Ask questions
    print("\n[3] Processing questions...")

    questions = [
        "What were the total Q3 laptop sales?",
        "Which region had the highest phone sales?",
        "Compare laptop sales to current inventory levels",
        "Should we reorder laptops based on sales velocity?"
    ]

    for i, question in enumerate(questions, 1):
        print(f"\n--- Question {i} ---")
        print(f"Q: {question}")

        try:
            # This will trigger decomposition for complex questions
            answer = await agent.process_question(question)
            print(f"A: {answer}")

        except NotImplementedError as e:
            print(f"⚠️  Not yet implemented: {e}")
            print("   (This is expected - complete the core components first)")

    # Step 4: View statistics
    print("\n[4] System Statistics")
    print("-" * 60)

    try:
        stats = agent.get_stats()
        print(f"Total Turns: {stats.total_turns}")
        print(f"Decompositions: {stats.total_decompositions}")
        print(f"Labels: {stats.total_labels}")
        print(f"Avg Sub-Questions: {stats.avg_sub_questions:.2f}")
        print(f"Total Data Size: {stats.total_size_kb:.2f} KB")

    except NotImplementedError:
        print("⚠️  Statistics not yet implemented")

    print("\n" + "=" * 60)
    print("Demo Complete!")
    print("=" * 60)


if __name__ == "__main__":
    asyncio.run(main())
