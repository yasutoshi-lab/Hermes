"""Agents package for Hermes.

Contains LangGraph workflow definition and node implementations
for the research and reporting pipeline.

The workflow orchestrates the complete research process:
1. Normalize user prompt
2. Generate search queries
3. Perform web research
4. Process content in container
5. Aggregate draft report
6. Validate and improve (loop)
7. Generate final report
"""

from .graph import create_hermes_workflow
from .state import HermesState

__all__ = [
    "create_hermes_workflow",
    "HermesState",
]
