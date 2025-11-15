# Container-use (Docker) Integration

## Overview

Container-use (via dagger-io) provides isolated text processing for Hermes. It runs normalization and processing tasks in disposable Docker containers for consistency and security.

Hermes automatically falls back to local processing when Docker is unavailable, ensuring the workflow always completes.

## Operational Modes

### Mode 1: Container Processing (Preferred)

- **Enabled**: When Docker is running
- **Technology**: dagger-io + Docker
- **Benefits**:
  - Isolated execution environment
  - Consistent processing across systems
  - No local dependency conflicts
  - Reproducible results
- **Requirements**:
  - Docker 20.10+ installed
  - Docker daemon running
  - User in docker group (Linux)

### Mode 2: Local Fallback (Automatic)

- **Enabled**: When Docker unavailable
- **Technology**: Native Python processing
- **Benefits**:
  - No Docker dependency
  - Faster execution (no container overhead)
  - Works in restricted environments
- **Limitations**:
  - Results may vary across systems
  - No execution isolation

## When Container Mode Matters

### Use Container Mode When:

- Production deployments
- Multi-user environments
- CI/CD pipelines
- Reproducibility is critical
- Security isolation required

### Local Mode is Acceptable When:

- Personal development
- Quick prototyping
- Docker unavailable (temporary)
- Simple text processing
- Single-user workstation

## Docker Installation

### Ubuntu/Debian

```bash
# Update package index
sudo apt-get update

# Install dependencies
sudo apt-get install -y \
    apt-transport-https \
    ca-certificates \
    curl \
    gnupg \
    lsb-release

# Add Docker's official GPG key
curl -fsSL https://download.docker.com/linux/ubuntu/gpg | sudo gpg --dearmor -o /usr/share/keyrings/docker-archive-keyring.gpg

# Set up stable repository
echo \
  "deb [arch=$(dpkg --print-architecture) signed-by=/usr/share/keyrings/docker-archive-keyring.gpg] https://download.docker.com/linux/ubuntu \
  $(lsb_release -cs) stable" | sudo tee /etc/apt/sources.list.d/docker.list > /dev/null

# Install Docker Engine
sudo apt-get update
sudo apt-get install -y docker-ce docker-ce-cli containerd.io docker-compose-plugin

# Verify installation
sudo docker run hello-world
```

### CentOS/RHEL

```bash
# Install required packages
sudo yum install -y yum-utils

# Add Docker repository
sudo yum-config-manager --add-repo https://download.docker.com/linux/centos/docker-ce.repo

# Install Docker
sudo yum install -y docker-ce docker-ce-cli containerd.io docker-compose-plugin

# Start Docker
sudo systemctl start docker
sudo systemctl enable docker

# Verify
sudo docker run hello-world
```

### macOS

```bash
# Option 1: Homebrew
brew install --cask docker

# Option 2: Download Docker Desktop
# Visit https://www.docker.com/products/docker-desktop

# Start Docker Desktop application

# Verify from terminal
docker run hello-world
```

### Windows (WSL2)

1. **Install WSL2**
   ```powershell
   wsl --install
   ```

2. **Install Docker Desktop**
   - Download from https://www.docker.com/products/docker-desktop
   - Enable WSL2 backend in settings

3. **Verify in WSL2**
   ```bash
   docker run hello-world
   ```

## Post-Installation Setup

### Linux: Add User to Docker Group

Running Docker without `sudo`:

```bash
# Add current user to docker group
sudo usermod -aG docker $USER

# Log out and back in for changes to take effect
# Or use newgrp
newgrp docker

# Verify (no sudo needed)
docker ps
```

### Enable Docker Service

```bash
# Start Docker daemon
sudo systemctl start docker

# Enable on boot
sudo systemctl enable docker

# Check status
sudo systemctl status docker
```

### Verify Installation

```bash
# Check Docker version
docker --version

# Check daemon status
docker info

# Run test container
docker run hello-world

# List running containers
docker ps

# List all containers
docker ps -a
```

## Hermes Integration

### Automatic Detection

Hermes automatically detects Docker availability:

```python
# Checks on each run
try:
    result = subprocess.run(["docker", "ps"], capture_output=True)
    if result.returncode == 0:
        # Use container mode
    else:
        # Fall back to local
except Exception:
    # Fall back to local
```

### Verify Container Mode

```bash
# Run a task
hermes run --prompt "test container" --max-validation 1

# Check logs for container usage
hermes log -n 50 | grep -i docker

# Expected: No warning message
# If fallback: "Docker is unavailable, using local processing"
```

### Force Local Mode

For testing or debugging:

```bash
# Stop Docker temporarily
sudo systemctl stop docker

# Run Hermes (will use fallback)
hermes run --prompt "..."

# Restart Docker
sudo systemctl start docker
```

## Container Lifecycle

### What Happens During Execution

1. **Container Creation**
   - Hermes requests container via dagger-io
   - Docker pulls required images (first time only)
   - Container starts with mounted volumes

2. **Processing**
   - Text normalization runs in isolation
   - Results returned to Hermes

3. **Cleanup**
   - Container stops automatically
   - Temporary data removed
   - Resources released

### Monitoring Containers

```bash
# Watch container activity during Hermes execution
watch -n 1 docker ps

# View container logs
docker logs <container_id>

# Check resource usage
docker stats
```

## Troubleshooting

### Docker Daemon Not Running

**Symptom**: "Cannot connect to the Docker daemon"

**Solutions**:

```bash
# Check daemon status
sudo systemctl status docker

# Start daemon
sudo systemctl start docker

# Enable on boot
sudo systemctl enable docker

# Verify
docker ps
```

### Permission Denied

**Symptom**: "permission denied while trying to connect to the Docker daemon socket"

**Cause**: User not in docker group

**Solution**:

```bash
# Add user to docker group
sudo usermod -aG docker $USER

# Apply changes (logout/login or use newgrp)
newgrp docker

# Verify
docker ps  # Should work without sudo
```

### Port Conflicts

**Symptom**: "port is already allocated"

**Solution**:

```bash
# Find process using the port
sudo lsof -i :PORT
sudo netstat -tulpn | grep PORT

# Kill process or change Hermes config
sudo kill <PID>
```

### Disk Space Issues

**Symptom**: "no space left on device"

**Check disk usage**:

```bash
# Check Docker disk usage
docker system df

# Check available space
df -h /var/lib/docker
```

**Clean up**:

```bash
# Remove unused containers
docker container prune

# Remove unused images
docker image prune

# Remove unused volumes
docker volume prune

# Remove everything unused
docker system prune -a

# Or specify amount to free
docker system prune -a --volumes --filter "until=24h"
```

### Image Pull Failures

**Symptom**: "Error response from daemon: pull access denied"

**Solutions**:

1. **Check internet connection**
   ```bash
   ping registry-1.docker.io
   ```

2. **Use different registry mirror**
   ```bash
   # Edit /etc/docker/daemon.json
   sudo tee /etc/docker/daemon.json > /dev/null <<EOF
   {
     "registry-mirrors": ["https://mirror.example.com"]
   }
   EOF

   sudo systemctl restart docker
   ```

3. **Pull manually**
   ```bash
   docker pull python:3.10-slim
   ```

### Container Start Failures

**Symptom**: "Error starting userland proxy"

**Solutions**:

1. **Restart Docker**
   ```bash
   sudo systemctl restart docker
   ```

2. **Check firewall**
   ```bash
   # UFW (Ubuntu)
   sudo ufw status
   sudo ufw allow docker

   # iptables
   sudo iptables -L -n
   ```

3. **Check SELinux (RHEL/CentOS)**
   ```bash
   getenforce
   # If 'Enforcing', temporarily set to Permissive for testing
   sudo setenforce 0
   ```

### Network Issues

**Symptom**: Containers can't reach internet

**Solutions**:

1. **Check Docker network**
   ```bash
   docker network ls
   docker network inspect bridge
   ```

2. **Test connectivity from container**
   ```bash
   docker run --rm alpine ping -c 3 8.8.8.8
   docker run --rm alpine ping -c 3 google.com
   ```

3. **Reset Docker network**
   ```bash
   sudo systemctl stop docker
   sudo ip link delete docker0
   sudo systemctl start docker
   ```

4. **Check DNS settings**
   ```bash
   # Edit /etc/docker/daemon.json
   sudo tee -a /etc/docker/daemon.json > /dev/null <<EOF
   {
     "dns": ["8.8.8.8", "8.8.4.4"]
   }
   EOF

   sudo systemctl restart docker
   ```

### Memory Limits

**Symptom**: "OOMKilled" in container logs

**Solution**:

```bash
# Check Docker memory limit
docker info | grep Memory

# Increase memory limit (Docker Desktop)
# Settings → Resources → Memory → Increase slider

# Or set memory limit per container (requires code change)
docker run --memory="2g" ...
```

### Slow Performance

**Symptom**: Container operations take too long

**Optimizations**:

1. **Use Docker volume mounts**
   ```bash
   # Check current mount type
   docker inspect <container_id> | grep -A 10 Mounts
   ```

2. **Prune unused resources**
   ```bash
   docker system prune
   ```

3. **Increase Docker resources** (macOS/Windows)
   - Docker Desktop → Settings → Resources
   - Increase CPUs and Memory

4. **Check disk performance**
   ```bash
   sudo iotop  # Monitor I/O
   ```

## Performance Tuning

### Resource Allocation

#### For Development (8 GB RAM System)

```bash
# Docker Desktop settings
CPUs: 2
Memory: 2 GB
Swap: 1 GB
```

#### For Production (16+ GB RAM System)

```bash
# Docker Desktop settings
CPUs: 4
Memory: 4 GB
Swap: 2 GB
```

### Image Optimization

Currently, Hermes uses default dagger images. Future optimizations:

- Pre-pull required images
- Use lighter base images
- Cache layers between runs

### Batch Processing

For `hermes queue`:

```bash
# Containers reused across tasks in same session
# No need to optimize individual task runs
hermes queue --all
```

## Monitoring and Logging

### Real-time Monitoring

```bash
# Watch container creation/deletion
watch -n 1 'docker ps --format "table {{.Names}}\t{{.Status}}\t{{.Image}}"'

# Monitor resource usage
docker stats

# View logs
docker logs -f <container_id>
```

### Hermes Integration Logs

```bash
# Check for container warnings
hermes debug -n 100 | grep -i docker

# Check for fallback activation
hermes log -n 50 | grep -i "using local"
```

### System Logs

```bash
# Docker daemon logs (systemd)
journalctl -u docker -f

# Docker daemon logs (file)
sudo tail -f /var/log/docker.log
```

## Security Considerations

### Container Isolation

Hermes containers run with default Docker security:

- Namespaced processes
- Limited filesystem access
- Network isolation (default bridge)
- Read-only root filesystem (when possible)

### Best Practices

1. **Keep Docker updated**
   ```bash
   sudo apt-get update && sudo apt-get upgrade docker-ce
   ```

2. **Don't run Docker as root** (use docker group)

3. **Limit container resources**
   ```bash
   # In future Hermes config
   container:
     memory_limit: 2g
     cpu_limit: 2
   ```

4. **Regular cleanup**
   ```bash
   # Weekly cron job
   0 2 * * 0 /usr/bin/docker system prune -af
   ```

### Network Security

```bash
# Restrict Docker API access
sudo chmod 660 /var/run/docker.sock

# Use TLS for remote Docker (if applicable)
# Configure in /etc/docker/daemon.json
```

## Advanced Configuration

### Docker Daemon Settings

Edit `/etc/docker/daemon.json`:

```json
{
  "log-driver": "json-file",
  "log-opts": {
    "max-size": "10m",
    "max-file": "3"
  },
  "storage-driver": "overlay2",
  "dns": ["8.8.8.8", "8.8.4.4"],
  "max-concurrent-downloads": 10,
  "max-concurrent-uploads": 5
}
```

Apply changes:

```bash
sudo systemctl restart docker
```

### Storage Driver Optimization

```bash
# Check current driver
docker info | grep "Storage Driver"

# Recommended: overlay2 (default on modern systems)

# Change driver (requires data migration)
# Edit /etc/docker/daemon.json
{
  "storage-driver": "overlay2"
}

# Restart Docker
sudo systemctl restart docker
```

## CI/CD Integration

### GitHub Actions Example

```yaml
name: Hermes Tests

on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest

    services:
      docker:
        image: docker:dind
        options: --privileged

    steps:
      - uses: actions/checkout@v2

      - name: Set up Docker
        run: |
          sudo systemctl start docker
          docker info

      - name: Install Hermes
        run: |
          pip install -e .

      - name: Test with containers
        run: |
          hermes run --prompt "CI test" --max-validation 1
```

### Docker-in-Docker (DinD)

For containerized CI environments:

```bash
# Run Hermes inside container that has Docker
docker run --privileged -v /var/run/docker.sock:/var/run/docker.sock \
  your-hermes-image hermes run --prompt "test"
```

## Maintenance

### Regular Tasks

#### Weekly

```bash
# Clean up unused resources
docker system prune -a --volumes

# Check disk usage
docker system df
```

#### Monthly

```bash
# Update Docker
sudo apt-get update && sudo apt-get upgrade docker-ce

# Verify health
docker info
docker run hello-world
```

#### As Needed

```bash
# Clear all Docker data (nuclear option)
docker system prune -a --volumes -f
sudo systemctl stop docker
sudo rm -rf /var/lib/docker
sudo systemctl start docker
```

## Uninstallation

### Remove Docker Engine (Linux)

```bash
# Stop Docker
sudo systemctl stop docker

# Remove packages
sudo apt-get purge docker-ce docker-ce-cli containerd.io docker-compose-plugin

# Remove Docker data
sudo rm -rf /var/lib/docker
sudo rm -rf /var/lib/containerd

# Remove Docker group
sudo groupdel docker
```

### Remove Docker Desktop (macOS/Windows)

- macOS: Drag Docker.app to Trash
- Windows: Uninstall via Control Panel

### Hermes Continues Working

After Docker removal, Hermes automatically uses local processing mode. No configuration changes needed.

## Comparison: Container vs Local Mode

| Aspect | Container Mode | Local Mode |
|--------|----------------|------------|
| **Setup** | Docker required | None |
| **Speed** | Slower (overhead) | Faster |
| **Isolation** | Yes | No |
| **Reproducibility** | High | Medium |
| **Disk Usage** | +1-2 GB | None |
| **Security** | Better | Good |
| **Maintenance** | Regular cleanup | None |

## Related Documentation

- [Ollama Integration](./ollama.md)
- [browser-use Integration](./browser-use.md)
- [Hermes Architecture](../../ARCHITECTURE.md)
- [Installation Guide](../../README.md#installation)

## External Resources

- [Docker Documentation](https://docs.docker.com/)
- [Dagger.io](https://dagger.io/)
- [Docker Best Practices](https://docs.docker.com/develop/dev-best-practices/)

## Support

For Docker-specific issues:
- Check `docker info` for configuration
- Review `journalctl -u docker` for daemon errors
- Test with `docker run hello-world`
- Check Hermes logs: `hermes debug --error -n 100 | grep -i docker`
