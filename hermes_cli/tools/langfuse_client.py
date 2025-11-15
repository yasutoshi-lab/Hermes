"""Langfuse tracing client for Hermes"""

from typing import Optional, Dict, Any
from loguru import logger
from langfuse import Langfuse


class LangfuseClient:
    """Langfuseトレーシングクライアント"""

    def __init__(
        self,
        enabled: bool = False,
        host: Optional[str] = None,
        public_key: Optional[str] = None,
        secret_key: Optional[str] = None,
    ):
        self.enabled = enabled
        self.client: Optional[Langfuse] = None
        self.current_trace = None

        if enabled and public_key and secret_key and host:
            try:
                self.client = Langfuse(
                    public_key=public_key,
                    secret_key=secret_key,
                    host=host,
                )
                logger.info(
                    f"Langfuse client initialized: {host}",
                    extra={"category": "LANGFUSE"},
                )
            except Exception as e:
                logger.warning(
                    f"Failed to initialize Langfuse client: {e}",
                    extra={"category": "LANGFUSE"},
                )
                self.enabled = False
        else:
            logger.info("Langfuse tracing disabled", extra={"category": "LANGFUSE"})

    def create_trace(
        self, name: str, metadata: Optional[Dict] = None, input_data: Optional[Any] = None
    ):
        """トレースを作成"""
        if not self.enabled or not self.client:
            return None

        try:
            self.current_trace = self.client.trace(
                name=name,
                metadata=metadata,
                input=input_data,
            )
            logger.debug(f"Trace created: {name}", extra={"category": "LANGFUSE"})
            return self.current_trace
        except Exception as e:
            logger.error(
                f"Failed to create trace: {e}", extra={"category": "LANGFUSE"}
            )
            return None

    def update_trace(self, output_data: Optional[Any] = None, metadata: Optional[Dict] = None):
        """トレースを更新"""
        if not self.enabled or not self.current_trace:
            return

        try:
            self.current_trace.update(
                output=output_data,
                metadata=metadata,
            )
        except Exception as e:
            logger.error(
                f"Failed to update trace: {e}", extra={"category": "LANGFUSE"}
            )

    def create_generation(
        self,
        name: str,
        model: str,
        input_data: Optional[Dict] = None,
        output_data: Optional[Dict] = None,
        metadata: Optional[Dict] = None,
    ):
        """LLM生成を記録"""
        if not self.enabled or not self.client:
            return None

        try:
            if self.current_trace:
                return self.current_trace.generation(
                    name=name,
                    model=model,
                    input=input_data,
                    output=output_data,
                    metadata=metadata,
                )
            else:
                return self.client.generation(
                    name=name,
                    model=model,
                    input=input_data,
                    output=output_data,
                    metadata=metadata,
                )
        except Exception as e:
            logger.error(
                f"Failed to create generation: {e}",
                extra={"category": "LANGFUSE"},
            )
            return None

    def flush(self) -> None:
        """バッファをフラッシュ"""
        if self.enabled and self.client:
            try:
                self.client.flush()
            except Exception as e:
                logger.error(
                    f"Failed to flush Langfuse: {e}", extra={"category": "LANGFUSE"}
                )
