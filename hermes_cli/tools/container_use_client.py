"""
Container execution client for isolated processing.

Provides a pragmatic wrapper that prefers running normalization inside a disposable
Python container (via the Docker CLI) and gracefully falls back to local processing
when container tools are unavailable.
"""

from typing import List, Dict, Any
import logging
import json
import shutil
import subprocess
import unicodedata
import re


DOCKER_NORMALIZER_SCRIPT = r"""
import json, re, unicodedata, sys
texts = json.loads(sys.stdin.read())
normalized = []
pattern = re.compile(r"\s+")
for text in texts:
    value = unicodedata.normalize("NFKC", text or "")
    value = pattern.sub(" ", value).strip()
    normalized.append(value)
print(json.dumps(normalized))
"""


class ContainerUseClient:
    """Client for containerized processing using docker/podman style runtimes."""

    def __init__(self, docker_image: str = "python:3.11-slim"):
        """Initialize container client."""
        self.logger = logging.getLogger(__name__)
        self.docker_path = shutil.which("docker")
        self.docker_image = docker_image
        self.docker_timeout = 45

        if self.docker_path:
            self.logger.info(
                "Initialized ContainerUseClient with Docker binary at %s", self.docker_path
            )
        else:
            self.logger.info(
                "Docker CLI not detected; ContainerUseClient will use local normalization."
            )

    def normalize_texts(self, texts: List[str]) -> List[str]:
        """
        Normalize and preprocess texts in container environment.

        This runs text processing tasks in an isolated container to ensure
        consistent results and security.

        Args:
            texts: List of raw text content to process

        Returns:
            List of normalized/processed texts

        Raises:
            ContainerUseError: On container execution failure
        """
        self.logger.info("Normalizing %s text(s)", len(texts))

        if self.docker_path:
            try:
                return self._normalize_with_docker(texts)
            except ContainerUseError as exc:
                self.logger.warning(
                    "Container normalization failed (%s); falling back to local processing",
                    exc,
                )

        normalized = self._normalize_locally(texts)
        self.logger.info("Successfully normalized %s text(s) locally", len(normalized))
        return normalized

    def execute_script(
        self, script: str, inputs: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Execute arbitrary script in container environment.

        Args:
            script: Script content to execute
            inputs: Input data for the script

        Returns:
            Output data from script execution

        Raises:
            ContainerUseError: On container execution failure
        """
        self.logger.info(
            f"Executing script in container with {len(inputs)} input(s)"
        )

        try:
            # TODO: Implement actual dagger-io integration
            # When dagger-io is available, implement:
            # 1. Create container with appropriate runtime
            # 2. Mount script and input data
            # 3. Execute script in isolated environment
            # 4. Extract output data and return

            # Placeholder implementation
            self.logger.warning(
                "Generic container script execution is not available yet."
            )

            # Example structure when dagger-io is implemented:
            # container = (
            #     self.dagger_client.container()
            #     .from_("python:3.10-slim")
            #     .with_new_file("/script.py", contents=script)
            #     .with_env_variable("INPUTS", json.dumps(inputs))
            #     .with_exec(["python", "/script.py"])
            # )
            # output_json = container.stdout()
            # return json.loads(output_json)

            return {
                "status": "not_implemented",
                "message": "dagger-io integration pending"
            }

        except Exception as e:
            self.logger.error(f"Script execution failed: {str(e)}")
            raise ContainerUseError(f"Failed to execute script: {str(e)}")

    def close(self):
        """Clean up container resources."""
        self.logger.debug("Closing ContainerUseClient")

    def __enter__(self):
        """Context manager entry."""
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit."""
        self.close()

    # Internal helpers -------------------------------------------------

    def _normalize_with_docker(self, texts: List[str]) -> List[str]:
        """Run normalization script inside a short-lived Python container."""
        if not self.docker_path:
            raise ContainerUseError("Docker CLI not available")

        payload = json.dumps(texts or [])
        cmd = [
            self.docker_path,
            "run",
            "--rm",
            "-i",
            self.docker_image,
            "python",
            "-c",
            DOCKER_NORMALIZER_SCRIPT,
        ]

        try:
            completed = subprocess.run(
                cmd,
                input=payload.encode("utf-8"),
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                check=True,
                timeout=self.docker_timeout,
            )
        except FileNotFoundError as exc:
            raise ContainerUseError("Docker binary not found") from exc
        except subprocess.CalledProcessError as exc:
            self.logger.error(
                "Docker normalization failed: %s", exc.stderr.decode("utf-8", errors="ignore")
            )
            raise ContainerUseError("Docker normalization command failed") from exc
        except subprocess.TimeoutExpired as exc:
            raise ContainerUseError("Docker normalization timed out") from exc

        try:
            output = completed.stdout.decode("utf-8")
            return json.loads(output)
        except json.JSONDecodeError as exc:
            raise ContainerUseError("Invalid normalization output") from exc

    def _normalize_locally(self, texts: List[str]) -> List[str]:
        """Deterministic normalization fallback used when containers are unavailable."""
        normalized: List[str] = []
        pattern = re.compile(r"\s+")

        for text in texts:
            value = unicodedata.normalize("NFKC", text or "")
            value = pattern.sub(" ", value).strip()
            normalized.append(value)

        return normalized


class ContainerUseError(Exception):
    """Raised when container execution fails."""
    pass
