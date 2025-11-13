"""
Container Manager Module

This module provides a wrapper for Docker-based container operations, offering
isolated execution environments for processing search results and running analysis
code safely. It implements the container-use pattern for the Hermes system.
"""

import docker
import tempfile
import uuid
from pathlib import Path
from typing import Dict, List, Optional, Any
from datetime import datetime
import logging
import tarfile
import io
import time


# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class ContainerError(Exception):
    """Base exception for container operations."""
    pass


class ContainerNotFoundError(ContainerError):
    """Raised when a container ID is not found."""
    pass


class ContainerExecutionError(ContainerError):
    """Raised when command execution in container fails."""
    pass


class ContainerManager:
    """
    Manages Docker containers for isolated processing tasks.

    This class provides functionality to create, manage, and clean up Docker
    containers for safe execution of data processing and analysis tasks.
    Each container is isolated and can be safely destroyed if errors occur.

    Attributes:
        client: Docker client instance
        containers: Dict mapping task IDs to container objects
        default_image: Default Docker image to use for containers
        resource_limits: Default resource limits (CPU, memory, timeout)
    """

    def __init__(
        self,
        default_image: str = "python:3.10-slim",
        max_cpu: float = 1.0,
        max_memory: str = "512m",
        default_timeout: int = 300
    ):
        """
        Initialize the ContainerManager.

        Args:
            default_image: Docker image to use (default: python:3.10-slim)
            max_cpu: Maximum CPU allocation (default: 1.0 core)
            max_memory: Maximum memory allocation (default: 512m)
            default_timeout: Default command timeout in seconds (default: 300)

        Raises:
            ContainerError: If Docker daemon is not available
        """
        try:
            self.client = docker.from_env()
            # Test connection
            self.client.ping()
        except Exception as e:
            raise ContainerError(f"Failed to connect to Docker daemon: {e}")

        self.containers: Dict[str, Any] = {}
        self.default_image = default_image
        self.max_cpu = max_cpu
        self.max_memory = max_memory
        self.default_timeout = default_timeout

        # Ensure default image is available
        self._ensure_image(default_image)

        logger.info(f"ContainerManager initialized with image: {default_image}")

    def _ensure_image(self, image: str) -> None:
        """
        Ensure Docker image is available, pull if necessary.

        Args:
            image: Docker image name

        Raises:
            ContainerError: If image cannot be pulled
        """
        try:
            self.client.images.get(image)
            logger.info(f"Image {image} already available")
        except docker.errors.ImageNotFound:
            logger.info(f"Pulling image {image}...")
            try:
                self.client.images.pull(image)
                logger.info(f"Successfully pulled image {image}")
            except Exception as e:
                raise ContainerError(f"Failed to pull image {image}: {e}")

    def create_container(self, task_id: str, image: Optional[str] = None) -> str:
        """
        Create an isolated container for a task.

        Args:
            task_id: Unique identifier for the task
            image: Docker image to use (optional, uses default if not specified)

        Returns:
            str: Container ID

        Raises:
            ContainerError: If container creation fails
        """
        if task_id in self.containers:
            logger.warning(f"Container for task {task_id} already exists")
            return self.containers[task_id].id

        image_name = image or self.default_image
        self._ensure_image(image_name)

        try:
            # Create container with resource limits
            container = self.client.containers.create(
                image=image_name,
                command="sleep infinity",  # Keep container running
                detach=True,
                mem_limit=self.max_memory,
                cpu_quota=int(self.max_cpu * 100000),
                cpu_period=100000,
                name=f"hermes-{task_id}-{uuid.uuid4().hex[:8]}",
                labels={
                    "hermes.task_id": task_id,
                    "hermes.created_at": datetime.now().isoformat()
                },
                network_mode="none"  # Disable network for security
            )

            container.start()
            self.containers[task_id] = container

            logger.info(f"Created container {container.id[:12]} for task {task_id}")
            return container.id

        except Exception as e:
            raise ContainerError(f"Failed to create container for task {task_id}: {e}")

    def _get_container(self, container_id: str) -> Any:
        """
        Get container object by ID.

        Args:
            container_id: Container ID or task ID

        Returns:
            Container object

        Raises:
            ContainerNotFoundError: If container not found
        """
        # Try to find by container ID first
        for task_id, container in self.containers.items():
            if container.id == container_id or task_id == container_id:
                return container

        # Try to reload from Docker
        try:
            container = self.client.containers.get(container_id)
            return container
        except docker.errors.NotFound:
            raise ContainerNotFoundError(f"Container {container_id} not found")

    def execute_in_container(
        self,
        container_id: str,
        command: str,
        timeout: Optional[int] = None,
        workdir: str = "/workspace"
    ) -> Dict[str, Any]:
        """
        Execute a command in the container.

        Args:
            container_id: Container ID or task ID
            command: Command to execute
            timeout: Command timeout in seconds (uses default if None)
            workdir: Working directory in container

        Returns:
            Dict containing:
                - exit_code: Command exit code
                - stdout: Standard output
                - stderr: Standard error
                - execution_time: Execution time in seconds

        Raises:
            ContainerNotFoundError: If container not found
            ContainerExecutionError: If execution fails
        """
        container = self._get_container(container_id)
        timeout = timeout or self.default_timeout

        try:
            start_time = time.time()

            # Execute command
            result = container.exec_run(
                cmd=f"sh -c 'cd {workdir} && {command}'",
                demux=True,
                environment={"PYTHONUNBUFFERED": "1"}
            )

            execution_time = time.time() - start_time

            # Handle output
            exit_code = result.exit_code
            stdout_bytes, stderr_bytes = result.output

            stdout = stdout_bytes.decode('utf-8', errors='replace') if stdout_bytes else ""
            stderr = stderr_bytes.decode('utf-8', errors='replace') if stderr_bytes else ""

            logger.info(
                f"Executed command in container {container.id[:12]}: "
                f"exit_code={exit_code}, time={execution_time:.2f}s"
            )

            return {
                "exit_code": exit_code,
                "stdout": stdout,
                "stderr": stderr,
                "execution_time": execution_time
            }

        except Exception as e:
            raise ContainerExecutionError(
                f"Failed to execute command in container {container_id}: {e}"
            )

    def execute_python_code(
        self,
        container_id: str,
        code: str,
        timeout: Optional[int] = None
    ) -> Dict[str, Any]:
        """
        Execute Python code in the container.

        Args:
            container_id: Container ID or task ID
            code: Python code to execute
            timeout: Execution timeout in seconds

        Returns:
            Dict with execution results (exit_code, stdout, stderr, execution_time)

        Raises:
            ContainerNotFoundError: If container not found
            ContainerExecutionError: If execution fails
        """
        # Escape code for shell execution
        escaped_code = code.replace("'", "'\"'\"'")
        command = f"python3 -c '{escaped_code}'"

        return self.execute_in_container(container_id, command, timeout)

    def copy_file_to_container(
        self,
        container_id: str,
        local_path: str,
        container_path: str
    ) -> None:
        """
        Copy a file from local filesystem to container.

        Args:
            container_id: Container ID or task ID
            local_path: Path to local file
            container_path: Destination path in container

        Raises:
            ContainerNotFoundError: If container not found
            ContainerError: If copy operation fails
        """
        container = self._get_container(container_id)
        local_file = Path(local_path)

        if not local_file.exists():
            raise ContainerError(f"Local file not found: {local_path}")

        try:
            # Create tar archive of file
            tar_stream = io.BytesIO()
            with tarfile.open(fileobj=tar_stream, mode='w') as tar:
                tar.add(local_file, arcname=Path(container_path).name)

            tar_stream.seek(0)

            # Put archive in container
            dest_dir = str(Path(container_path).parent)
            container.put_archive(dest_dir, tar_stream.read())

            logger.info(
                f"Copied {local_path} to {container_path} "
                f"in container {container.id[:12]}"
            )

        except Exception as e:
            raise ContainerError(
                f"Failed to copy file to container {container_id}: {e}"
            )

    def copy_file_from_container(
        self,
        container_id: str,
        container_path: str,
        local_path: str
    ) -> None:
        """
        Copy a file from container to local filesystem.

        Args:
            container_id: Container ID or task ID
            container_path: Source path in container
            local_path: Destination path on local filesystem

        Raises:
            ContainerNotFoundError: If container not found
            ContainerError: If copy operation fails
        """
        container = self._get_container(container_id)

        try:
            # Get archive from container
            bits, stat = container.get_archive(container_path)

            # Extract archive
            tar_stream = io.BytesIO()
            for chunk in bits:
                tar_stream.write(chunk)
            tar_stream.seek(0)

            # Extract to local path
            with tarfile.open(fileobj=tar_stream) as tar:
                # Extract file
                member = tar.getmembers()[0]
                extracted = tar.extractfile(member)
                if extracted:
                    Path(local_path).parent.mkdir(parents=True, exist_ok=True)
                    with open(local_path, 'wb') as f:
                        f.write(extracted.read())

            logger.info(
                f"Copied {container_path} from container {container.id[:12]} "
                f"to {local_path}"
            )

        except Exception as e:
            raise ContainerError(
                f"Failed to copy file from container {container_id}: {e}"
            )

    def get_container_logs(self, container_id: str) -> str:
        """
        Retrieve container execution logs.

        Args:
            container_id: Container ID or task ID

        Returns:
            str: Container logs

        Raises:
            ContainerNotFoundError: If container not found
        """
        container = self._get_container(container_id)

        try:
            logs = container.logs().decode('utf-8', errors='replace')
            return logs
        except Exception as e:
            raise ContainerError(f"Failed to get logs for container {container_id}: {e}")

    def cleanup_container(self, container_id: str, force: bool = True) -> None:
        """
        Remove container and associated resources.

        Args:
            container_id: Container ID or task ID
            force: Force removal even if container is running

        Raises:
            ContainerNotFoundError: If container not found
            ContainerError: If cleanup fails
        """
        container = self._get_container(container_id)

        try:
            # Stop container if running
            if container.status == 'running':
                container.stop(timeout=5)

            # Remove container
            container.remove(force=force)

            # Remove from tracking
            for task_id, tracked_container in list(self.containers.items()):
                if tracked_container.id == container.id:
                    del self.containers[task_id]
                    break

            logger.info(f"Cleaned up container {container.id[:12]}")

        except Exception as e:
            raise ContainerError(f"Failed to cleanup container {container_id}: {e}")

    def list_containers(self) -> List[Dict[str, Any]]:
        """
        List all active containers managed by this instance.

        Returns:
            List of dicts with container information:
                - id: Container ID
                - task_id: Associated task ID
                - status: Container status
                - created_at: Creation timestamp
                - image: Docker image name
        """
        containers_info = []

        for task_id, container in self.containers.items():
            try:
                container.reload()  # Refresh status
                containers_info.append({
                    "id": container.id,
                    "task_id": task_id,
                    "status": container.status,
                    "created_at": container.labels.get('hermes.created_at', 'unknown'),
                    "image": container.image.tags[0] if container.image.tags else 'unknown'
                })
            except Exception as e:
                logger.warning(f"Failed to get info for container {task_id}: {e}")

        return containers_info

    def cleanup_all(self) -> int:
        """
        Clean up all containers managed by this instance.

        Returns:
            int: Number of containers cleaned up
        """
        count = 0
        for task_id in list(self.containers.keys()):
            try:
                self.cleanup_container(task_id)
                count += 1
            except Exception as e:
                logger.error(f"Failed to cleanup container for task {task_id}: {e}")

        logger.info(f"Cleaned up {count} containers")
        return count

    def install_packages(self, container_id: str, packages: List[str]) -> Dict[str, Any]:
        """
        Install Python packages in the container.

        Args:
            container_id: Container ID or task ID
            packages: List of package names to install

        Returns:
            Dict with installation results

        Raises:
            ContainerExecutionError: If installation fails
        """
        if not packages:
            return {"exit_code": 0, "stdout": "No packages to install", "stderr": ""}

        package_list = " ".join(packages)
        command = f"pip install --no-cache-dir {package_list}"

        return self.execute_in_container(container_id, command, timeout=600)

    def __enter__(self):
        """Context manager entry."""
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit - cleanup all containers."""
        self.cleanup_all()

    def __del__(self):
        """Destructor - attempt cleanup on deletion."""
        try:
            self.cleanup_all()
        except:
            pass
