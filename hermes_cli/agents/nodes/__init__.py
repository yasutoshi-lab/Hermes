"""Workflow nodes for Hermes agents"""

from hermes_cli.agents.nodes.prompt_normalizer import normalize_prompt
from hermes_cli.agents.nodes.query_generator import generate_queries
from hermes_cli.agents.nodes.web_researcher import search_web
from hermes_cli.agents.nodes.container_processor import process_contents
from hermes_cli.agents.nodes.draft_aggregator import create_draft
from hermes_cli.agents.nodes.validator import validate_report
from hermes_cli.agents.nodes.validation_controller import should_continue_validation
from hermes_cli.agents.nodes.final_reporter import finalize_report

__all__ = [
    "normalize_prompt",
    "generate_queries",
    "search_web",
    "process_contents",
    "create_draft",
    "validate_report",
    "should_continue_validation",
    "finalize_report",
]
