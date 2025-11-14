"""State model for Hermes agent workflow.

This module defines the Pydantic state model used throughout the LangGraph workflow,
tracking all data from user input through query generation, research, processing,
validation, and final report generation.
"""

from typing import Dict, List, Optional
from pydantic import BaseModel, Field


class HermesState(BaseModel):
    """State model for Hermes agent workflow.

    This state is passed through all nodes in the LangGraph workflow,
    accumulating data and tracking progress through the research pipeline.

    Attributes:
        user_prompt: Original user query/prompt
        language: Output language (ja/en)
        queries: Generated search queries
        query_results: Search results per query
        processed_notes: Normalized text per query
        draft_report: Current draft report
        validated_report: Final validated report
        loop_count: Current validation loop iteration
        min_validation: Minimum validation loops
        max_validation: Maximum validation loops
        validation_complete: Validation completion flag
        min_sources: Minimum sources per query
        max_sources: Maximum sources per query
        error_log: Error messages collected during workflow
    """

    # Input
    user_prompt: str = Field(description="Original user query/prompt")
    language: str = Field(default="ja", description="Output language (ja/en)")

    # Query generation
    queries: List[str] = Field(default_factory=list, description="Generated search queries")

    # Research results
    query_results: Dict[str, List[dict]] = Field(
        default_factory=dict,
        description="Search results per query: {query: [results]}"
    )

    # Processed data
    processed_notes: Dict[str, str] = Field(
        default_factory=dict,
        description="Normalized text per query: {query: processed_text}"
    )

    # Report drafts
    draft_report: Optional[str] = Field(default=None, description="Current draft report")
    validated_report: Optional[str] = Field(default=None, description="Final validated report")

    # Validation control
    loop_count: int = Field(default=0, description="Current validation loop iteration")
    min_validation: int = Field(default=1, description="Minimum validation loops")
    max_validation: int = Field(default=3, description="Maximum validation loops")
    validation_complete: bool = Field(default=False, description="Validation completion flag")

    # Configuration
    min_sources: int = Field(default=3, description="Minimum sources per query")
    max_sources: int = Field(default=8, description="Maximum sources per query")

    # Metadata
    error_log: List[str] = Field(default_factory=list, description="Error messages")

    class Config:
        """Pydantic configuration."""
        arbitrary_types_allowed = True
