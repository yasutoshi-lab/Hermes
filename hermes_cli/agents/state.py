"""State model for Hermes agent workflow.

This module defines the Pydantic state model used throughout the LangGraph workflow,
tracking all data from user input through query generation, research, processing,
validation, and final report generation.
"""

from __future__ import annotations

from typing import Callable, Dict, List, Optional
from pydantic import BaseModel, Field

from hermes_cli.tools.ollama_client import OllamaClient, OllamaConfig


class HermesState(BaseModel):
    """State model for Hermes agent workflow.

    This state is passed through all nodes in the LangGraph workflow,
    accumulating data and tracking progress through the research pipeline.

    Attributes:
        user_prompt: Original user query/prompt
        language: Output language (ja/en)
        queries: Generated baseline search queries
        follow_up_queries: Validator-generated follow-up queries awaiting execution
        executed_queries: Ordered list of all queries actually executed
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
        quality_score: Heuristic quality measurement used by validation controller
        quality_threshold: Threshold above which validation can stop
        error_log: Error messages collected during workflow
    """

    # Input
    user_prompt: str = Field(description="Original user query/prompt")
    language: str = Field(default="ja", description="Output language (ja/en)")
    query_count: int = Field(default=3, description="Target number of queries to generate")

    # Query generation
    queries: List[str] = Field(default_factory=list, description="Generated baseline search queries")
    follow_up_queries: List[str] = Field(
        default_factory=list,
        description="Validator-suggested follow-up queries awaiting execution",
    )
    executed_queries: List[str] = Field(
        default_factory=list,
        description="All queries that have been executed (baseline + follow-ups)",
    )

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
    quality_score: float = Field(default=0.0, description="Heuristic validation quality score")
    quality_threshold: float = Field(default=0.7, description="Score required to finish validation")

    # LLM configuration
    ollama_config: Optional[OllamaConfig] = Field(
        default=None,
        description="Resolved Ollama client configuration",
    )
    ollama_client_factory: Optional[Callable[["OllamaConfig"], "OllamaClient"]] = Field(
        default=None,
        exclude=True,
        description="Factory for creating Ollama clients (supports testing stubs)",
    )

    class Config:
        """Pydantic configuration."""
        arbitrary_types_allowed = True

    # --- Helper methods -------------------------------------------------

    def build_chat_messages(
        self,
        system_prompt: Optional[str],
        user_prompt: str,
    ) -> List[Dict[str, str]]:
        """Return chat-formatted messages for Ollama."""
        messages: List[Dict[str, str]] = []

        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})

        messages.append({"role": "user", "content": user_prompt})
        return messages

    def create_ollama_client(self):
        """Instantiate an Ollama client using the stored factory/config."""
        if not self.ollama_client_factory or not self.ollama_config:
            raise RuntimeError("Ollama client factory or config is not configured in state")
        return self.ollama_client_factory(self.ollama_config)

    def call_ollama(
        self,
        system_prompt: Optional[str],
        user_prompt: str,
    ) -> str:
        """Convenience helper to execute an Ollama chat call."""
        with self.create_ollama_client() as client:
            messages = self.build_chat_messages(system_prompt, user_prompt)
            return client.chat(messages)


# Resolve forward references for Pydantic BaseModel
HermesState.model_rebuild()
