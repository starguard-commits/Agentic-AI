"""
Data Models for Context Decomposition Strategy

This module defines all core data structures used throughout the system.
Uses Pydantic for validation and serialization.
"""

from typing import List, Optional, Any, Dict
from pydantic import BaseModel, Field
from datetime import datetime


class SubQuestion(BaseModel):
    """
    Represents a single sub-question from decomposition.

    Attributes:
        id: Unique identifier (e.g., "Q1", "Q2")
        text: The actual question text
        labels: List of label IDs required for this sub-question
        depends_on: List of sub-question IDs this depends on

    Example:
        SubQuestion(
            id="Q1",
            text="What were Q3 laptop sales?",
            labels=["sales_q3", "laptops"],
            depends_on=[]
        )
    """
    id: str = Field(..., description="Unique sub-question ID")
    text: str = Field(..., description="Question text")
    labels: List[str] = Field(default_factory=list, description="Required label IDs")
    depends_on: List[str] = Field(default_factory=list, description="Dependencies")


class Decomposition(BaseModel):
    """
    Represents the decomposition of a question into sub-questions.

    Returned by DecompositionEngine after breaking down a complex question.

    Attributes:
        original_question: The original user question
        sub_questions: List of SubQuestion objects
        created_at: When this decomposition was created
    """
    original_question: str = Field(..., description="Original question")
    sub_questions: List[SubQuestion] = Field(..., description="List of sub-questions")
    created_at: datetime = Field(default_factory=datetime.now)

    def get_independent_questions(self) -> List[SubQuestion]:
        """Return sub-questions with no dependencies."""
        # TODO: Implement filtering logic
        return [sq for sq in self.sub_questions if not sq.depends_on]

    def get_dependent_questions(self) -> List[SubQuestion]:
        """Return sub-questions that have dependencies."""
        # TODO: Implement filtering logic
        return [sq for sq in self.sub_questions if sq.depends_on]


class ExecutionWave(BaseModel):
    """
    Represents a wave of sub-questions that can execute in parallel.

    All sub-questions in a wave have their dependencies satisfied
    by previous waves.

    Attributes:
        wave_number: Sequential wave number (0, 1, 2, ...)
        sub_questions: List of SubQuestion objects in this wave
    """
    wave_number: int = Field(..., description="Wave sequence number")
    sub_questions: List[SubQuestion] = Field(..., description="Sub-questions in this wave")


class ExecutionPlan(BaseModel):
    """
    Complete execution plan with ordered waves.

    Produced by ExecutionPlanner from a Decomposition.

    Attributes:
        waves: Ordered list of ExecutionWave objects
        total_sub_questions: Total number of sub-questions
    """
    waves: List[ExecutionWave] = Field(..., description="Execution waves")

    @property
    def total_sub_questions(self) -> int:
        """Calculate total number of sub-questions across all waves."""
        # TODO: Implement calculation
        return sum(len(wave.sub_questions) for wave in self.waves)


class Label(BaseModel):
    """
    Represents a labeled context chunk.

    Labels are stored in SQLite and fetched during execution.

    Attributes:
        id: Unique label identifier
        clause_summary: Brief telegraphic summary for LLM
        data: The actual data (JSON serializable)
        size_kb: Size in kilobytes
        metadata: Additional metadata (access count, created_turn, etc.)

    Example:
        Label(
            id="sales_q3",
            clause_summary="Q3 2024 sales data, all products, regional breakdown",
            data={"laptops": {...}, "phones": {...}},
            size_kb=15.3
        )
    """
    id: str = Field(..., description="Label ID")
    clause_summary: str = Field(..., description="Brief summary for LLM")
    data: Any = Field(..., description="Actual data (any JSON-serializable type)")
    size_kb: float = Field(default=0.0, description="Size in KB")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Metadata")


class TurnMetrics(BaseModel):
    """
    Metrics for a single conversation turn.

    Used for analytics and submission reporting.

    Attributes:
        turn_id: Turn number
        was_decomposed: Whether decomposition was triggered
        num_sub_questions: Number of sub-questions (if decomposed)
        token_count: Total tokens used
        labels_accessed: List of label IDs accessed
        execution_time_ms: Wall-clock execution time
    """
    turn_id: int
    was_decomposed: bool = False
    num_sub_questions: Optional[int] = None
    token_count: int = 0
    labels_accessed: List[str] = Field(default_factory=list)
    execution_time_ms: Optional[float] = None


class SystemStats(BaseModel):
    """
    Overall system statistics for reporting.

    Attributes:
        total_turns: Total conversation turns
        total_decompositions: Number of times decomposition was used
        total_labels: Number of labels in store
        avg_sub_questions: Average sub-questions per decomposition
        total_size_kb: Total size of all labels
        most_accessed_labels: Top N most accessed labels
    """
    total_turns: int = 0
    total_decompositions: int = 0
    total_labels: int = 0
    avg_sub_questions: float = 0.0
    total_size_kb: float = 0.0
    most_accessed_labels: List[str] = Field(default_factory=list)

    def to_report_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for JSON export."""
        # TODO: Implement conversion
        return self.model_dump()
