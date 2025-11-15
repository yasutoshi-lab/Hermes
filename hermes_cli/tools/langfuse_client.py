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
        self, name: str, user_id: Optional[str] = None, metadata: Optional[Dict] = None
    ) -> Optional[Any]:
        """トレース作成"""
        if not self.enabled or not self.client:
            return None

        try:
            trace = self.client.trace(
                name=name,
                user_id=user_id,
                metadata=metadata or {},
            )
            return trace
        except Exception as e:
            logger.error(
                f"Failed to create trace: {e}", extra={"category": "LANGFUSE"}
            )
            return None

    def create_span(
        self,
        trace_id: str,
        name: str,
        input_data: Optional[Dict] = None,
        metadata: Optional[Dict] = None,
    ) -> Optional[Any]:
        """スパン作成"""
        if not self.enabled or not self.client:
            return None

        try:
            span = self.client.span(
                trace_id=trace_id,
                name=name,
                input=input_data,
                metadata=metadata or {},
            )
            return span
        except Exception as e:
            logger.error(
                f"Failed to create span: {e}", extra={"category": "LANGFUSE"}
            )
            return None

    def update_span(
        self,
        span_id: str,
        output_data: Optional[Dict] = None,
        metadata: Optional[Dict] = None,
        level: str = "DEFAULT",
    ) -> None:
        """スパン更新"""
        if not self.enabled or not self.client:
            return

        try:
            self.client.span(
                id=span_id,
                output=output_data,
                metadata=metadata,
                level=level,
            )
        except Exception as e:
            logger.error(
                f"Failed to update span: {e}", extra={"category": "LANGFUSE"}
            )

    def log_generation(
        self,
        trace_id: str,
        name: str,
        model: str,
        input_data: Any,
        output_data: Any,
        metadata: Optional[Dict] = None,
    ) -> None:
        """LLM生成ログ"""
        if not self.enabled or not self.client:
            return

        try:
            self.client.generation(
                trace_id=trace_id,
                name=name,
                model=model,
                input=input_data,
                output=output_data,
                metadata=metadata or {},
            )
        except Exception as e:
            logger.error(
                f"Failed to log generation: {e}", extra={"category": "LANGFUSE"}
            )

    def flush(self) -> None:
        """バッファをフラッシュ"""
        if self.enabled and self.client:
            try:
                self.client.flush()
            except Exception as e:
                logger.error(
                    f"Failed to flush Langfuse: {e}", extra={"category": "LANGFUSE"}
                )
