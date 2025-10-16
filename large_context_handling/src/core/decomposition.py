"""
Decomposition Engine - Phase 1 of the 3-phase strategy

Decomposes complex questions into sub-questions with label requirements.
"""

import json
from typing import List, Dict, Optional
from src.models.data_models import Decomposition, SubQuestion
from src.models.prompts import DECOMPOSITION_PROMPT
from src.llm.client import LLMClient


class DecompositionEngine:
    """
    Phase 1: Question Decomposition with Label Selection.

    Responsibilities:
    - Build decomposition prompt with available labels
    - Call LLM for decomposition
    - Parse JSON response into Decomposition object
    - Validate decomposition (dependencies, label refs)

    Example:
        engine = DecompositionEngine(llm_client)
        decomp = engine.decompose(
            question="Compare Q3 sales to inventory",
            label_summaries=["L1: sales data", "L2: inventory data"]
        )
    """

    def __init__(self, llm_client: LLMClient):
        """
        Initialize decomposition engine.

        Args:
            llm_client: LLM client for API calls
        """
        self.llm = llm_client

    def decompose(
        self,
        question: str,
        label_summaries: List[str],
        context_limit: int = 100000
    ) -> Decomposition:
        """
        Decompose question into sub-questions.

        Args:
            question: User's question
            label_summaries: List of "id: summary" strings
            context_limit: Token limit for guidance

        Returns:
            Decomposition object with sub-questions

        Raises:
            DecompositionError: If decomposition fails

        TODO: Implement decomposition
        - Build prompt using DECOMPOSITION_PROMPT template
        - Call LLM (with JSON mode if available)
        - Parse response into SubQuestion objects
        - Validate decomposition
        - Return Decomposition object
        """
        # TODO: Implement
        raise NotImplementedError("Decomposition not yet implemented")

    def _build_decomposition_prompt(
        self,
        question: str,
        labels: List[str]
    ) -> str:
        """
        Build decomposition prompt from template.

        Args:
            question: User question
            labels: Label summaries

        Returns:
            Formatted prompt string

        TODO: Implement prompt formatting
        - Format label summaries (numbered list)
        - Insert into DECOMPOSITION_PROMPT template
        - Return formatted string
        """
        # TODO: Implement
        pass

    def _parse_decomposition(self, llm_response: str) -> Decomposition:
        """
        Parse LLM response into Decomposition object.

        Args:
            llm_response: Raw LLM output (expected JSON)

        Returns:
            Decomposition object

        Raises:
            ValueError: If parsing fails

        TODO: Implement parsing
        - Extract JSON from response
        - Parse sub_questions array
        - Create SubQuestion objects
        - Create Decomposition object
        - Handle parsing errors gracefully
        """
        # TODO: Implement
        pass

    def _validate_decomposition(
        self,
        decomposition: Decomposition,
        valid_label_ids: List[str]
    ) -> bool:
        """
        Validate decomposition for correctness.

        Args:
            decomposition: Decomposition to validate
            valid_label_ids: List of valid label IDs

        Returns:
            True if valid

        Raises:
            ValueError: If validation fails

        TODO: Implement validation
        - Check no circular dependencies
        - Verify all label IDs exist in valid_label_ids
        - Ensure dependency IDs reference valid sub-questions
        - Check sub-questions have unique IDs
        """
        # TODO: Implement
        pass

    def _detect_circular_dependencies(
        self,
        sub_questions: List[SubQuestion]
    ) -> bool:
        """
        Detect circular dependencies in sub-questions.

        Args:
            sub_questions: List of SubQuestion objects

        Returns:
            True if circular dependency exists

        TODO: Implement cycle detection
        - Build dependency graph
        - Use DFS to detect cycles
        - Return True if cycle found
        """
        # TODO: Implement
        pass
