"""
Input node for accepting user queries and configuration.

This is the entry point of the LangGraph workflow, responsible for:
- Extracting user queries from messages
- Detecting input language
- Validating input
- Initializing session history
- Setting default configuration values
"""

import logging
from typing import Any, Dict, Literal, Optional

from config import settings
from modules.history_manager import HistoryManager, HistoryManagerError
from modules.language_detector import LanguageDetector
from state.agent_state import AgentState, add_error

# Configure logging
logger = logging.getLogger(__name__)


class InputPreparationError(Exception):
    """Raised when the input node cannot prepare the initial context."""


def _normalize_language_code(language: Optional[str]) -> Optional[Literal["ja", "en"]]:
    """
    Normalize arbitrary language strings to internal codes.
    """
    if not language or not isinstance(language, str):
        return None

    value = language.strip().lower()
    if value in {"ja", "jp", "japanese", "日本語"}:
        return "ja"
    if value in {"en", "eng", "english"}:
        return "en"
    return None


def _format_localized_message(language: Literal["ja", "en"], ja_text: str, en_text: str) -> str:
    """
    Helper to choose localized text for system messages.
    """
    return ja_text if language == "ja" else en_text


def _build_session_message(
    language: Literal["ja", "en"],
    model_name: str,
    confidence: float,
    detection_source: str
) -> str:
    """
    Create a localized session bootstrap message.
    """
    if language == "ja":
        if detection_source == "user":
            language_part = "ユーザー指定の日本語設定"
        else:
            language_part = f"自動判定: 日本語 (信頼度 {confidence:.2f})"
        return f"セッションを開始しました。使用モデル: {model_name} / 言語: {language_part}"

    if detection_source == "user":
        language_part = "user-provided English preference"
    else:
        language_part = f"auto-detected English (confidence {confidence:.2f})"
    return f"Session started. Using model: {model_name}. Language: {language_part}"


def prepare_initial_context(
    messages: list[dict],
    *,
    language: Optional[str] = None,
    model_name: Optional[str] = None,
    history_path: Optional[str] = None,
    detector: Optional[LanguageDetector] = None,
    history_manager: Optional[HistoryManager] = None,
    default_language: Optional[Literal["ja", "en"]] = None,
    default_model: Optional[str] = None
) -> Dict[str, Any]:
    """
    Shared helper that prepares query, language, model, and history context.

    This function encapsulates the normalization logic so that CLI/interactive
    entry points can reuse the same behavior as the LangGraph InputNode.

    Returns:
        Dict with the prepared values and helper metadata:
            - query
            - language
            - model_name
            - history_path
            - system_messages (list of dict for LangGraph reducer)
            - language_confidence
            - warnings (list of warning strings)
    """
    if not isinstance(messages, list) or not messages:
        raise InputPreparationError("No input messages provided")

    try:
        raw_query = extract_query_from_messages(messages)
    except ValueError as exc:
        raise InputPreparationError(str(exc)) from exc

    query = clean_and_normalize_text(raw_query)
    if not query:
        raise InputPreparationError("Query is empty after cleaning")

    resolved_default_language = default_language or settings.default_language
    resolved_default_model = (default_model or settings.default_model).strip()

    normalized_language = _normalize_language_code(language)
    detector_instance = detector or LanguageDetector(default_language=resolved_default_language)

    if normalized_language:
        resolved_language: Literal["ja", "en"] = normalized_language
        confidence = 1.0
        detection_source = "user"
    else:
        resolved_language, confidence = detector_instance.detect_with_confidence(query)
        detection_source = "auto"

    # Model handling
    provided_model = model_name.strip() if isinstance(model_name, str) else ""
    if provided_model and validate_model_name(provided_model):
        resolved_model = provided_model
    else:
        resolved_model = resolved_default_model

    warnings: list[str] = []
    resolved_history_path = (history_path or "").strip()

    if not resolved_history_path:
        history_manager_instance = history_manager or HistoryManager(base_path=settings.session_storage_path)
        try:
            session_id = history_manager_instance.create_session()
            resolved_history_path = str(history_manager_instance.base_path / session_id)
            history_manager_instance.save_input(
                session_id,
                query,
                {
                    "language": resolved_language,
                    "model_name": resolved_model,
                    "default_language": resolved_default_language,
                    "default_model": resolved_default_model
                }
            )
        except HistoryManagerError as exc:
            warning = f"History session could not be initialized ({exc})"
            warnings.append(warning)
            logger.warning("InputNode: %s", warning)
            resolved_history_path = ""
        except Exception as exc:  # pragma: no cover - unexpected I/O failure
            warning = f"History session could not be initialized ({exc})"
            warnings.append(warning)
            logger.warning("InputNode: %s", warning)
            resolved_history_path = ""

    system_message = _build_session_message(
        resolved_language,
        resolved_model,
        confidence,
        detection_source
    )

    system_messages = [
        {"role": "system", "content": system_message}
    ]

    return {
        "query": query,
        "language": resolved_language,
        "model_name": resolved_model,
        "history_path": resolved_history_path,
        "system_messages": system_messages,
        "language_confidence": confidence,
        "warnings": warnings,
    }


def extract_query_from_messages(messages: list[dict]) -> str:
    """
    Extract the user query from message history.

    Args:
        messages: List of message dictionaries with 'role' and 'content' keys

    Returns:
        Extracted query string (last user message)

    Raises:
        ValueError: If no user messages found
    """
    if not messages:
        raise ValueError("No messages provided")

    # Find the last user message
    for message in reversed(messages):
        if message.get("role") == "user":
            content = message.get("content", "").strip()
            if content:
                return content

    raise ValueError("No user message found in message history")


def clean_and_normalize_text(text: str) -> str:
    """
    Clean and normalize input text.

    Args:
        text: Raw input text

    Returns:
        Cleaned and normalized text
    """
    # Remove excessive whitespace
    text = " ".join(text.split())

    # Remove leading/trailing whitespace
    text = text.strip()

    return text


def validate_model_name(model_name: str) -> bool:
    """
    Validate if model name is non-empty and follows basic format.

    Args:
        model_name: Model name to validate

    Returns:
        True if valid, False otherwise
    """
    if not model_name or not isinstance(model_name, str):
        return False

    # Basic validation: non-empty string without special chars that might cause issues
    if model_name.strip() and len(model_name) > 0:
        return True

    return False


def input_node(
    state: AgentState,
    history_manager: Optional[HistoryManager] = None
) -> Dict[str, Any]:
    """
    Process user input and initialize the agent state.

    This node is the entry point of the workflow. It:
    1. Extracts the user query from messages
    2. Cleans and normalizes the input
    3. Detects the language (Japanese or English)
    4. Validates input and configuration
    5. Creates a new session for history tracking
    6. Saves initial input to history
    7. Returns updated state with all initialized values

    Args:
        state: Current agent state with initial messages

    Returns:
        Updated state dict with:
        - query: Extracted and cleaned user query
        - language: Detected language ('ja' or 'en')
        - model_name: Validated model name
        - history_path: Session storage path
        - messages: Updated with any system messages
        - errors: List of any errors encountered

    Example:
        >>> state = {
        ...     "messages": [{"role": "user", "content": "LangGraphとは何ですか？"}],
        ...     "language": "",
        ...     "model_name": "",
        ...     ...
        ... }
        >>> updates = input_node(state)
        >>> updates['query']
        'LangGraphとは何ですか？'
        >>> updates['language']
        'ja'
    """
    logger.info("InputNode: Processing user input")

    try:
        prepared = prepare_initial_context(
            state.get("messages", []),
            language=state.get("language"),
            model_name=state.get("model_name"),
            history_path=state.get("history_path"),
            history_manager=history_manager,
        )
    except InputPreparationError as exc:
        error_msg = f"Failed to prepare input: {exc}"
        logger.error("InputNode: %s", error_msg)
        return add_error(state, error_msg)
    except Exception as exc:
        error_msg = f"Unexpected error in InputNode: {exc}"
        logger.exception("InputNode: %s", error_msg)
        return add_error(state, error_msg)

    system_messages = list(prepared["system_messages"])
    for warning in prepared.get("warnings", []):
        warning_text = _format_localized_message(
            prepared["language"],
            f"警告: {warning}",
            f"Warning: {warning}"
        )
        system_messages.append({"role": "system", "content": warning_text})

    result = {
        "query": prepared["query"],
        "language": prepared["language"],
        "model_name": prepared["model_name"],
        "history_path": prepared["history_path"],
        "messages": system_messages,
    }

    logger.info(
        "InputNode: Successfully processed input [lang=%s, model=%s, history=%s]",
        prepared["language"],
        prepared["model_name"],
        prepared["history_path"] or "disabled"
    )

    return result
