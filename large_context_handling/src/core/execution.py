"""
Execution Module - Phase 2 of the 3-phase strategy

Contains ExecutionPlanner and ParallelExecutor.
"""

import asyncio
from typing import List, Dict, Optional
from src.models.data_models import (
    Decomposition,
    ExecutionPlan,
    ExecutionWave,
    SubQuestion
)
from src.models.prompts import EXECUTION_PROMPT, format_dependency_results
from src.llm.client import LLMClient
from src.core.label_store import LabelStore


class ExecutionPlanner:
    """
    Plans execution of sub-questions based on dependencies.

    Responsibilities:
    - Build dependency graph
    - Detect circular dependencies
    - Compute execution waves (topological sort)
    - Group independent sub-questions

    Example:
        planner = ExecutionPlanner()
        plan = planner.build_execution_plan(decomposition)
        # plan.waves = [Wave1: [Q1, Q2], Wave2: [Q3]]
    """

    def build_execution_plan(
        self,
        decomposition: Decomposition
    ) -> ExecutionPlan:
        """
        Build execution plan from decomposition.

        Args:
            decomposition: Decomposition with sub-questions

        Returns:
            ExecutionPlan with ordered waves

        TODO: Implement execution planning
        - Build dependency graph
        - Compute waves (MVP: 2-wave, Future: full topological sort)
        - Create ExecutionWave objects
        - Return ExecutionPlan
        """
        # TODO: Implement
        raise NotImplementedError("Execution planning not yet implemented")

    def _build_dependency_graph(
        self,
        decomposition: Decomposition
    ) -> Dict[str, List[str]]:
        """
        Build dependency graph from sub-questions.

        Args:
            decomposition: Decomposition object

        Returns:
            Dict mapping sub-question ID to list of dependencies

        TODO: Implement graph construction
        - For each sub-question, extract dependencies
        - Build adjacency list representation
        - Return graph dict
        """
        # TODO: Implement
        pass

    def _compute_execution_waves(
        self,
        graph: Dict[str, List[str]],
        sub_questions: List[SubQuestion]
    ) -> List[ExecutionWave]:
        """
        Compute execution waves from dependency graph.

        MVP: Two waves (independent, then dependent)
        Future: Full topological sort for optimal parallelization

        Args:
            graph: Dependency graph
            sub_questions: List of SubQuestion objects

        Returns:
            List of ExecutionWave objects

        TODO: Implement wave computation
        - MVP: Separate into independent and dependent waves
        - Future: Full topological sort with multiple waves
        """
        # TODO: Implement
        pass


class ParallelExecutor:
    """
    Phase 2: Execute sub-questions with context isolation.

    Responsibilities:
    - Execute waves sequentially
    - Execute sub-questions within wave in parallel (asyncio)
    - Fetch required labels for each sub-question
    - Handle errors gracefully
    - Collect and return results

    Example:
        executor = ParallelExecutor(llm_client, label_store)
        results = await executor.execute_wave(wave1, previous_results={})
        # results = {"Q1": "answer1", "Q2": "answer2"}
    """

    def __init__(
        self,
        llm_client: LLMClient,
        label_store: LabelStore
    ):
        """
        Initialize parallel executor.

        Args:
            llm_client: LLM client for API calls
            label_store: Label store for fetching context
        """
        self.llm = llm_client
        self.labels = label_store

    async def execute_wave(
        self,
        wave: ExecutionWave,
        previous_results: Dict[str, str],
        current_turn: int
    ) -> Dict[str, str]:
        """
        Execute a wave of sub-questions in parallel.

        Args:
            wave: ExecutionWave with sub-questions
            previous_results: Results from previous waves
            current_turn: Current turn number

        Returns:
            Dict mapping sub-question IDs to answers

        TODO: Implement wave execution
        - Create async tasks for each sub-question
        - Use asyncio.gather() for parallel execution
        - Handle individual failures gracefully
        - Return results dict
        """
        # TODO: Implement
        raise NotImplementedError("Wave execution not yet implemented")

    async def _execute_sub_question(
        self,
        sub_q: SubQuestion,
        previous_results: Dict[str, str],
        current_turn: int
    ) -> str:
        """
        Execute a single sub-question with context isolation.

        Args:
            sub_q: SubQuestion to execute
            previous_results: Results from dependencies
            current_turn: Current turn number

        Returns:
            Answer string

        TODO: Implement sub-question execution
        - Fetch required labels from label_store
        - Add dependency results (if any)
        - Build execution prompt
        - Call LLM (async)
        - Return answer
        """
        # TODO: Implement
        pass

    def _build_execution_prompt(
        self,
        sub_q: SubQuestion,
        context: List[Dict],
        dependency_results: Dict[str, str]
    ) -> str:
        """
        Build execution prompt for sub-question.

        Args:
            sub_q: SubQuestion object
            context: List of label data dicts
            dependency_results: Results from dependencies

        Returns:
            Formatted prompt string

        TODO: Implement prompt building
        - Format context data
        - Format dependency results (if any)
        - Insert into EXECUTION_PROMPT template
        - Return formatted prompt
        """
        # TODO: Implement
        pass

    def _handle_execution_error(
        self,
        sub_q: SubQuestion,
        error: Exception
    ) -> str:
        """
        Handle execution error for a sub-question.

        Args:
            sub_q: SubQuestion that failed
            error: The exception

        Returns:
            Error message to include in results

        TODO: Implement error handling
        - Log error
        - Decide: retry, skip, or fail fast?
        - Return descriptive error message
        """
        # TODO: Implement
        pass
