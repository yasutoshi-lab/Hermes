# Hermes External Dependencies

This directory contains detailed documentation for Hermes' external dependencies and integrations.

## Overview

Hermes relies on three external systems for its research capabilities:

| Dependency | Status | Purpose | Documentation |
|------------|--------|---------|---------------|
| **Ollama** | Required | LLM inference for text generation | [ollama.md](./ollama.md) |
| **Docker** | Optional | Container isolation for processing | [container-use.md](./container-use.md) |
| **browser-use** | Optional | Enhanced web automation | [browser-use.md](./browser-use.md) |

## Quick Setup Guide

### Minimal Setup (Required Only)

For basic Hermes functionality:

```bash
# 1. Install Ollama
curl -fsSL https://ollama.ai/install.sh | sh

# 2. Pull model
ollama serve &
ollama pull gpt-oss:20b

# 3. Install Hermes
pip install -e .

# 4. Initialize
hermes init

# 5. Test
hermes run --prompt "test query" --max-validation 1
```

**Features enabled**:
- ✅ LLM-powered text generation
- ✅ DuckDuckGo web search
- ✅ Local text processing
- ❌ Container isolation
- ❌ Advanced browser automation

### Full Setup (All Features)

For complete functionality:

```bash
# 1. Install Ollama (see above)

# 2. Install Docker
# Ubuntu/Debian
sudo apt-get update
sudo apt-get install docker.io
sudo systemctl start docker
sudo usermod -aG docker $USER

# 3. Install browser-use
cd /tmp
git clone https://github.com/browser-use/browser-use.git
cd browser-use
pip install -e .
playwright install chromium

# 4. Install Hermes with extras
cd /path/to/Hermes
pip install -e .[browser,dev]

# 5. Initialize and test
hermes init
hermes run --prompt "comprehensive test" --max-validation 2
```

**Features enabled**:
- ✅ LLM-powered text generation
- ✅ Enhanced web search with browser-use
- ✅ Container-based processing
- ✅ Full automation capabilities

## Dependency Matrix

### By Operating System

| OS | Ollama | Docker | browser-use |
|----|--------|--------|-------------|
| Ubuntu 20.04+ | ✅ Native | ✅ Native | ✅ Supported |
| Ubuntu 18.04 | ✅ Native | ✅ Native | ⚠️ Manual setup |
| Debian 11+ | ✅ Native | ✅ Native | ✅ Supported |
| CentOS 8+ | ✅ Native | ✅ Native | ✅ Supported |
| macOS 11+ | ✅ Native | ✅ Docker Desktop | ✅ Supported |
| macOS 10.15 | ✅ Native | ⚠️ Docker Desktop | ⚠️ Limited |
| Windows 11 (WSL2) | ✅ Via WSL2 | ✅ Docker Desktop | ✅ Via WSL2 |
| Windows 10 (WSL2) | ✅ Via WSL2 | ✅ Docker Desktop | ✅ Via WSL2 |

✅ Fully supported | ⚠️ Requires additional setup | ❌ Not supported

### By Hardware

| Hardware | Ollama | Docker | browser-use | Recommended Config |
|----------|--------|--------|-------------|--------------------|
| 8 GB RAM, No GPU | ⚠️ Small models | ✅ Limited | ✅ Yes | llama2:7b, 2 loops |
| 16 GB RAM, No GPU | ✅ Medium models | ✅ Good | ✅ Yes | llama2:13b, 3 loops |
| 32 GB RAM, GPU 8 GB | ✅ Large models | ✅ Excellent | ✅ Yes | gpt-oss:20b, 5 loops |
| 64+ GB RAM, GPU 16+ GB | ✅ Any model | ✅ Excellent | ✅ Yes | llama2:70b, unlimited |

## Dependency Decision Tree

### When to Install Docker?

```
Need reproducible results? ───Yes─→ Install Docker
         │
         No
         │
Single-user development? ───Yes─→ Skip Docker (use local mode)
         │
         No
         │
CI/CD environment? ───Yes─→ Install Docker
         │
         No
         │
Production deployment? ───Yes─→ Install Docker
         │
         No
         │
         └─→ Skip Docker (use local mode)
```

### When to Install browser-use?

```
Need JavaScript rendering? ───Yes─→ Install browser-use
         │
         No
         │
Scraping dynamic sites? ───Yes─→ Install browser-use
         │
         No
         │
DuckDuckGo sufficient? ───Yes─→ Skip browser-use
         │
         No
         │
         └─→ Try DuckDuckGo first, install browser-use if needed
```

## Installation Order

Recommended installation sequence:

1. **Ollama** (required, install first)
2. **Hermes base** (required)
3. **Docker** (optional, for container mode)
4. **browser-use** (optional, for enhanced search)

This order ensures dependencies are available when needed.

## Verification Checklist

After installation, verify each component:

### ✅ Ollama

```bash
# Check server
curl http://localhost:11434/api/version

# Check model
ollama list | grep gpt-oss

# Test generation
ollama run gpt-oss:20b "Hello"
```

### ✅ Docker

```bash
# Check daemon
docker info

# Check permissions
docker ps

# Test container
docker run hello-world
```

### ✅ browser-use

```bash
# Check installation
python -c "import browser_use; print('OK')"

# Check Playwright
playwright --version

# Test browser
playwright open chromium
```

### ✅ Hermes Integration

```bash
# Full test
hermes run --prompt "integration test" --max-validation 1

# Check logs
hermes log -n 50 | grep -E "(ollama|docker|browser)"
```

## Common Setup Scenarios

### Scenario 1: Developer Laptop (8 GB RAM)

**Goal**: Fast development with minimal overhead

```bash
# Install Ollama + small model
ollama pull mistral:7b

# Install Hermes only
pip install -e .

# Configure for speed
# ~/.hermes/config.yaml
ollama:
  model: mistral:7b
  timeout_sec: 120
validation:
  max_loops: 2
search:
  max_sources: 5
```

**Skip**: Docker, browser-use

### Scenario 2: Research Workstation (32 GB RAM + GPU)

**Goal**: Maximum quality and features

```bash
# Install everything
ollama pull gpt-oss:20b
sudo apt-get install docker.io
cd /tmp && git clone https://github.com/browser-use/browser-use.git
cd browser-use && pip install -e .
playwright install chromium
pip install -e .[browser,dev]

# Configure for quality
# ~/.hermes/config.yaml
ollama:
  model: gpt-oss:20b
  timeout_sec: 300
validation:
  max_loops: 5
search:
  max_sources: 12
```

### Scenario 3: CI/CD Pipeline

**Goal**: Reproducible automated testing

```bash
# In Dockerfile or CI script
RUN curl -fsSL https://ollama.ai/install.sh | sh
RUN ollama serve & sleep 5 && ollama pull llama2:7b

# Install Docker-in-Docker
RUN apt-get install -y docker.io

# Skip browser-use (not needed for most tests)

# Configure for CI
ENV HERMES_MAX_VALIDATION=1
ENV HERMES_MAX_SOURCES=3
```

### Scenario 4: Production Server (Batch Processing)

**Goal**: Stable overnight batch runs

```bash
# Install all components
# Use systemd services for auto-restart

# Ollama service
sudo systemctl enable ollama

# Docker service
sudo systemctl enable docker

# Configure for reliability
# ~/.hermes/config.yaml
ollama:
  model: llama2:13b  # Balance speed/quality
  timeout_sec: 240
  retry: 5  # More retries
validation:
  max_loops: 3
search:
  max_sources: 8
```

## Troubleshooting Quick Reference

### Ollama Issues

| Symptom | Quick Fix | Documentation |
|---------|-----------|---------------|
| Connection refused | `ollama serve &` | [ollama.md](./ollama.md#connection-refused) |
| Model not found | `ollama pull gpt-oss:20b` | [ollama.md](./ollama.md#model-not-found-404-error) |
| Timeout | Increase `timeout_sec` | [ollama.md](./ollama.md#timeout-errors) |
| Slow performance | Use smaller model | [ollama.md](./ollama.md#slow-performance) |

### Docker Issues

| Symptom | Quick Fix | Documentation |
|---------|-----------|---------------|
| Daemon not running | `sudo systemctl start docker` | [container-use.md](./container-use.md#docker-daemon-not-running) |
| Permission denied | `sudo usermod -aG docker $USER` | [container-use.md](./container-use.md#permission-denied) |
| Disk space | `docker system prune -a` | [container-use.md](./container-use.md#disk-space-issues) |
| Network issues | Check DNS settings | [container-use.md](./container-use.md#network-issues) |

### browser-use Issues

| Symptom | Quick Fix | Documentation |
|---------|-----------|---------------|
| Not detected | Reinstall from source | [browser-use.md](./browser-use.md#browser-use-not-detected) |
| Playwright error | `playwright install chromium` | [browser-use.md](./browser-use.md#playwright-installation-failed) |
| Browser launch fails | Install system deps | [browser-use.md](./browser-use.md#browser-launch-failures) |
| Rate limiting | Wait 2 minutes, retry | [browser-use.md](./browser-use.md#rate-limiting) |

## Performance Optimization Guide

### By Use Case

#### Quick Tests (Development)

```yaml
# Minimize everything
ollama:
  model: mistral:7b
  timeout_sec: 60
validation:
  min_loops: 1
  max_loops: 1
search:
  max_sources: 3
```

**Disable**: Docker, browser-use

**Expected time**: 30-60 seconds per task

#### Balanced Quality (Default)

```yaml
# Current defaults
ollama:
  model: gpt-oss:20b
  timeout_sec: 180
validation:
  min_loops: 1
  max_loops: 3
search:
  max_sources: 8
```

**Enable**: Docker (optional), DuckDuckGo only

**Expected time**: 2-4 minutes per task

#### Maximum Quality (Research)

```yaml
# All features, highest quality
ollama:
  model: llama2:70b
  timeout_sec: 300
validation:
  min_loops: 3
  max_loops: 7
search:
  max_sources: 15
```

**Enable**: Docker, browser-use

**Expected time**: 10-20 minutes per task

## Upgrade Path

### From Minimal to Full Setup

```bash
# 1. Already have: Ollama + Hermes

# 2. Add Docker
sudo apt-get install docker.io
sudo systemctl start docker
sudo usermod -aG docker $USER
# Logout/login

# 3. Add browser-use
cd /tmp && git clone https://github.com/browser-use/browser-use.git
cd browser-use && pip install -e .
playwright install chromium

# 4. Test incremental improvements
hermes run --prompt "upgrade test" --max-validation 2
```

### Downgrade (Remove Optional Components)

```bash
# Remove browser-use
pip uninstall browser-use

# Stop/disable Docker
sudo systemctl stop docker
sudo systemctl disable docker

# Hermes automatically falls back
# No configuration changes needed
```

## Maintenance Schedule

### Daily (Automated)

- Check Ollama service status
- Monitor disk space

### Weekly (Manual)

```bash
# Clean Docker resources
docker system prune -a

# Check logs
hermes debug --error -n 500 | grep -E "(ollama|docker|browser)"

# Test all components
hermes run --prompt "weekly health check" --max-validation 1
```

### Monthly (Manual)

```bash
# Update Ollama
curl -fsSL https://ollama.ai/install.sh | sh

# Update Docker
sudo apt-get update && sudo apt-get upgrade docker-ce

# Update browser-use
cd /tmp/browser-use && git pull && pip install -e .

# Update Playwright
playwright install chromium

# Full integration test
hermes run --prompt "monthly verification" --max-validation 3
```

## Resource Planning

### Disk Space Requirements

| Component | Initial | Growth Rate | Notes |
|-----------|---------|-------------|-------|
| Ollama | 10 GB | +5 GB per model | Models in `~/.ollama/` |
| Docker | 2 GB | +1 GB/month | Images and containers |
| browser-use | 300 MB | Minimal | Playwright browsers |
| Hermes data | 100 MB | +10 MB/day | Reports and logs in `~/.hermes/` |

**Total**: 12-15 GB initially, +10-50 MB/day ongoing

### Memory Requirements

| Workload | Ollama | Docker | browser-use | Total |
|----------|--------|--------|-------------|-------|
| Idle | 500 MB | 200 MB | 0 MB | 700 MB |
| Single task | 4-8 GB | 500 MB | 200 MB | 5-9 GB |
| Queue processing | 4-8 GB | 500 MB | 200 MB | 5-9 GB |

**Recommendation**: 16 GB RAM for comfortable operation

## Related Documentation

- [Main README](../../README.md) - Project overview
- [Installation Guide](../../README.md#installation)
- [Integration Setup](../../README.md#integration-setup)
- [Command Reference](../command/README.md)
- [Troubleshooting](../../README.md#troubleshooting-highlights)

## External Resources

- [Ollama Documentation](https://github.com/ollama/ollama)
- [Docker Documentation](https://docs.docker.com/)
- [browser-use GitHub](https://github.com/browser-use/browser-use)
- [Playwright Documentation](https://playwright.dev/)

## Support

For dependency-specific issues:

1. **Check logs**: `hermes debug --error -n 200`
2. **Test components individually** using commands in verification checklist
3. **Review detailed documentation** for specific dependency
4. **Check external project issue trackers** for known issues

For Hermes integration issues:

- Review [Troubleshooting Guide](../../README.md#troubleshooting-highlights)
- Check [Architecture Documentation](../../ARCHITECTURE.md)
- Report with full logs: `hermes debug -n 500 > debug.log`
