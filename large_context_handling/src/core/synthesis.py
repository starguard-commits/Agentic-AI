"""
Synthesis Engine - Phase 3 of the 3-phase strategy

Synthesizes final answer from sub-question results.
"""

from typing import Dict
from src.models.data_models import Decomposition
from src.models.prompts import (
    SYNTHESIS_PROMPT,
    format_decomposition_summary,
    format_results_summary
)
from src.llm.client import LLMClient


class SynthesisEngine:
    """
    Phase 3: Synthesize final answer from sub-answers.

    Responsibilities:
    - Build synthesis prompt with original question + sub-results
    - Call LLM for synthesis
    - Handle potential contradictions
    - Return final comprehensive answer

    Example:
        engine = SynthesisEngine(llm_client)
        answer = engine.synthesize(
            question="Compare Q3 sales to inventory",
            decomposition=decomp,
            results={"Q1": "...", "Q2": "...", "Q3": "..."}
        )
    """

    def __init__(self, llm_client: LLMClient):
        """
        Initialize synthesis engine.

        Args:
            llm_client: LLM client for API calls
        """
        self.llm = llm_client

    def synthesize(
        self,
        original_question: str,
        decomposition: Decomposition,
        results: Dict[str, str]
    ) -> str:
        """
        Synthesize final answer from sub-answers.

        Args:
            original_question: The original user question
            decomposition: Decomposition object (for context)
            results: Dict mapping sub-question IDs to answers

        Returns:
            Final comprehensive answer string

        TODO: Implement synthesis
        - Build synthesis prompt
        - Call LLM
        - Parse and return final answer
        """
        # TODO: Implement
        raise NotImplementedError("Synthesis not yet implemented")

    def _build_synthesis_prompt(
        self,
        question: str,
        decomposition: Decomposition,
        results: Dict[str, str]
    ) -> str:
        """
        Build synthesis prompt from template.

        Args:
            question: Original question
            decomposition: Decomposition object
            results: Sub-question results

        Returns:
            Formatted prompt string

        TODO: Implement prompt building
        - Format decomposition summary
        - Format results summary
        - Insert into SYNTHESIS_PROMPT template
        - Return formatted prompt
        """
        # TODO: Implement
        pass

    def _check_for_contradictions(
        self,
        results: Dict[str, str]
    ) -> bool:
        """
        Check if sub-answers contain contradictions.

        Optional validation step before synthesis.

        Args:
            results: Sub-question results

        Returns:
            True if contradictions detected

        TODO: Implement contradiction detection
        - Use LLM or heuristics to detect conflicts
        - Return True if found
        - Consider logging warnings
        """
        # TODO: Implement (optional feature)
        pass
