"""
LLM Prompt Templates for Context Decomposition Strategy

This module contains all prompt templates used for:
- Question decomposition (Phase 1)
- Sub-question execution (Phase 2)
- Answer synthesis (Phase 3)
"""

DECOMPOSITION_PROMPT = """
You are a question decomposition specialist. Your task is to break down complex questions into simpler sub-questions for optimal context isolation.

ORIGINAL QUESTION:
{question}

AVAILABLE CONTEXT LABELS:
{label_summaries}

TASK:
Decompose the question into 2-5 sub-questions that:
1. Maximize context isolation (each uses minimal, non-overlapping labels)
2. Can be answered independently OR specify dependencies clearly
3. Minimize total token usage
4. Together fully answer the original question

OUTPUT FORMAT (JSON):
{{
  "sub_questions": [
    {{
      "id": "Q1",
      "text": "sub-question text here",
      "labels": ["label_id_1", "label_id_2"],
      "depends_on": []
    }},
    {{
      "id": "Q2",
      "text": "another sub-question",
      "labels": ["label_id_3"],
      "depends_on": ["Q1"]
    }}
  ]
}}

GUIDELINES:
- Use ONLY label IDs that appear in the available labels list
- Mark dependencies clearly (e.g., Q2 depends on Q1 if it needs Q1's answer)
- Prefer independent sub-questions when possible (enables parallelization)
- Keep sub-questions focused and specific
- Ensure complete coverage of the original question

Think step-by-step:
1. What information is needed to answer the question?
2. Which labels contain that information?
3. Can the question be broken into independent parts?
4. What dependencies exist between sub-questions?
"""


EXECUTION_PROMPT = """
You are answering a focused sub-question with specific context provided.

SUB-QUESTION:
{sub_question}

CONTEXT:
{context}

{dependency_results}

TASK:
Answer the sub-question using ONLY the provided context.

GUIDELINES:
- Be concise and specific
- Only use information from the provided context
- If context is insufficient, state what's missing
- Your answer will be used to synthesize a final comprehensive response
"""


SYNTHESIS_PROMPT = """
You previously decomposed a complex question into sub-questions. Now synthesize the final comprehensive answer.

ORIGINAL QUESTION:
{original_question}

YOUR DECOMPOSITION:
{decomposition_summary}

SUB-QUESTION RESULTS:
{results_summary}

TASK:
Provide a comprehensive, coherent answer to the original question using the sub-answers.

GUIDELINES:
- Integrate all sub-answers into a cohesive response
- Resolve any contradictions or inconsistencies
- Ensure complete coverage of the original question
- Maintain factual accuracy from sub-answers
- Present information in a logical, well-structured manner

If sub-answers are contradictory or incomplete:
- Note the discrepancies
- Explain what additional information would be needed
- Provide the best answer possible with available information
"""


# Helper function to format dependency results
def format_dependency_results(results: dict) -> str:
    """
    Format dependency results for inclusion in execution prompt.

    Args:
        results: Dict mapping sub-question IDs to their answers

    Returns:
        Formatted string for prompt

    TODO: Implement formatting logic
    """
    if not results:
        return ""

    formatted = "\n\nPREVIOUS SUB-QUESTION RESULTS:\n"
    for q_id, answer in results.items():
        formatted += f"{q_id}: {answer}\n\n"

    return formatted


def format_decomposition_summary(decomposition) -> str:
    """
    Format decomposition for synthesis prompt.

    Args:
        decomposition: Decomposition object

    Returns:
        Human-readable summary

    TODO: Implement formatting
    """
    summary = ""
    for sq in decomposition.sub_questions:
        summary += f"- {sq.id}: {sq.text}\n"
        if sq.labels:
            summary += f"  Labels: {', '.join(sq.labels)}\n"
        if sq.depends_on:
            summary += f"  Depends on: {', '.join(sq.depends_on)}\n"

    return summary


def format_results_summary(sub_questions, results: dict) -> str:
    """
    Format results for synthesis prompt.

    Args:
        sub_questions: List of SubQuestion objects
        results: Dict mapping sub-question IDs to answers

    Returns:
        Formatted results string

    TODO: Implement formatting
    """
    summary = ""
    for sq in sub_questions:
        answer = results.get(sq.id, "NO ANSWER")
        summary += f"\n{sq.id}: {sq.text}\n"
        summary += f"Answer: {answer}\n"

    return summary
