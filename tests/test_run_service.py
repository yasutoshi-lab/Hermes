from hermes_cli.agents import HermesState
from hermes_cli.persistence.config_repository import (
    Config,
    LoggingConfig,
    OllamaConfig,
    SearchConfig,
    ValidationConfig,
)
from hermes_cli.persistence.file_paths import FilePaths
from hermes_cli.services.run_service import RunService
from hermes_cli.tools.ollama_client import OllamaConfig as ToolOllamaConfig


class DummyWorkflow:
    def __init__(self):
        self.invoked_state = None

    def invoke(self, state: HermesState):
        self.invoked_state = state
        # Simulate minimal workflow artifacts
        state.query_results = {"q": [{"content": "stub"}]}
        state.validated_report = "# Completed"
        return state


class DummyConfigService:
    def __init__(self):
        self.config = Config(
            ollama=OllamaConfig(
                api_base="http://localhost:11434/api/chat",
                model="gpt-oss:20b",
                retry=3,
                timeout_sec=60,
            ),
            language="ja",
            validation=ValidationConfig(min_loops=1, max_loops=3),
            search=SearchConfig(min_sources=2, max_sources=5),
            logging=LoggingConfig(
                level="INFO",
                log_dir="~/.hermes/log",
                debug_log_dir="~/.hermes/debug_log",
            ),
            cli={"history_limit": 100},
        )

    def load(self):
        return self.config

    def apply_overrides(self, config: Config, overrides):
        language = overrides.get("language", config.language)
        min_val = overrides.get("min_validation", config.validation.min_loops)
        max_val = overrides.get("max_validation", config.validation.max_loops)

        new_config = Config(
            ollama=OllamaConfig(
                api_base=overrides.get("api", config.ollama.api_base),
                model=overrides.get("model", config.ollama.model),
                retry=overrides.get("retry", config.ollama.retry),
                timeout_sec=overrides.get("timeout", config.ollama.timeout_sec),
            ),
            language=language,
            validation=ValidationConfig(min_loops=min_val, max_loops=max_val),
            search=SearchConfig(
                min_sources=overrides.get("min_sources", config.search.min_sources),
                max_sources=overrides.get("max_sources", config.search.max_sources),
            ),
            logging=config.logging,
            cli=config.cli,
        )

        return new_config


def test_run_service_injects_ollama_context(monkeypatch, tmp_path):
    base = tmp_path / ".hermes"
    file_paths = FilePaths(base_path=base)
    file_paths.ensure_directories()

    factory_calls = []

    def stub_factory(config: ToolOllamaConfig):
        factory_calls.append(config)

        class StubClient:
            def __enter__(self):
                return self

            def __exit__(self, exc_type, exc_val, exc_tb):
                return False

            def chat(self, messages, stream=False):
                return "stub response"

        return StubClient()

    service = RunService(file_paths=file_paths, ollama_client_factory=stub_factory)
    service.config_service = DummyConfigService()

    dummy_workflow = DummyWorkflow()
    monkeypatch.setattr(
        "hermes_cli.services.run_service.create_hermes_workflow",
        lambda: dummy_workflow,
    )

    meta = service.run_prompt(
        prompt="Explain superconductors",
        options={"language": "en", "min_validation": 2, "query_count": 4, "model": "custom-model"},
    )

    state = dummy_workflow.invoked_state
    assert state.language == "en"
    assert state.query_count == 4
    assert state.ollama_config.model == "custom-model"
    assert state.ollama_client_factory is stub_factory
    assert meta.report_file.startswith("report-")
