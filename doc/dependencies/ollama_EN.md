# Ollama Integration

## Overview

Ollama is a local LLM inference server that powers Hermes' text generation capabilities. It handles:

- Search query generation
- Report drafting and synthesis
- Content validation and critique
- Follow-up query generation

Ollama is **required** for Hermes to function.

## System Requirements

### Minimum Requirements

- **CPU**: 4 cores (8+ recommended)
- **RAM**: 8 GB (16+ GB recommended)
- **Disk**: 10 GB free space for models
- **OS**: Linux, macOS, or Windows (WSL2)

### Recommended for gpt-oss:20b

- **CPU**: 8+ cores
- **RAM**: 32 GB
- **GPU**: NVIDIA GPU with 16+ GB VRAM (optional but significantly faster)
- **Disk**: 20 GB free space

### GPU Support

- **NVIDIA**: Requires CUDA 11.7+ drivers
- **AMD**: ROCm support on Linux
- **Apple Silicon**: Native Metal acceleration

## Installation

### Linux (Ubuntu/Debian)

```bash
# Download and install
curl -fsSL https://ollama.ai/install.sh | sh

# Verify installation
ollama --version
```

### macOS

```bash
# Option 1: Homebrew
brew install ollama

# Option 2: Direct download
# Download from https://ollama.ai/download
# Install the .dmg file

# Verify installation
ollama --version
```

### Windows (WSL2)

```bash
# Inside WSL2 Ubuntu
curl -fsSL https://ollama.ai/install.sh | sh

# Verify
ollama --version
```

### Docker (Alternative)

```bash
# Pull Ollama image
docker pull ollama/ollama

# Run server
docker run -d -v ollama:/root/.ollama -p 11434:11434 --name ollama ollama/ollama

# Verify
curl http://localhost:11434/api/version
```

## Model Setup

### Pull Required Model

Hermes defaults to `gpt-oss:20b`:

```bash
# Start Ollama server first
ollama serve &

# Pull model (13 GB download)
ollama pull gpt-oss:20b
```

This will download to `~/.ollama/models/`.

### Alternative Models

If `gpt-oss:20b` is unavailable, use these alternatives:

```bash
# Smaller, faster models
ollama pull llama2:7b      # 3.8 GB - Fast but lower quality
ollama pull llama2:13b     # 7.3 GB - Good balance
ollama pull mistral:7b     # 4.1 GB - Fast, good quality

# Larger, higher quality models
ollama pull llama2:70b     # 39 GB - Best quality, slower
ollama pull mixtral:8x7b   # 26 GB - High quality
```

Configure in `~/.hermes/config.yaml`:

```yaml
ollama:
  model: llama2:13b  # Change here
```

Or override per-run:

```bash
hermes run --prompt "..." --model llama2:13b
```

### List Installed Models

```bash
ollama list
```

### Remove Models

```bash
ollama rm gpt-oss:20b
```

## Starting the Server

### Background Service (Recommended)

```bash
# Start server in background
ollama serve &

# Check status
curl http://localhost:11434/api/version

# Expected output:
# {"version":"0.x.x"}
```

### Systemd Service (Linux)

```bash
# Create service file
sudo tee /etc/systemd/system/ollama.service > /dev/null <<EOF
[Unit]
Description=Ollama LLM Server
After=network.target

[Service]
Type=simple
User=$USER
ExecStart=/usr/local/bin/ollama serve
Restart=always
RestartSec=3

[Install]
WantedBy=multi-user.target
EOF

# Enable and start
sudo systemctl enable ollama
sudo systemctl start ollama

# Check status
sudo systemctl status ollama
```

### Docker Container

```bash
# Start container
docker start ollama

# View logs
docker logs -f ollama

# Stop container
docker stop ollama
```

## Configuration

### Default Settings

Ollama listens on `http://localhost:11434` by default.

### Custom Host/Port

```bash
# Set environment variable
export OLLAMA_HOST=0.0.0.0:11434

# Start server
ollama serve
```

### GPU Configuration

```bash
# Force CPU-only mode (if GPU issues)
export CUDA_VISIBLE_DEVICES=""
ollama serve

# Use specific GPU
export CUDA_VISIBLE_DEVICES=0
ollama serve

# Use multiple GPUs
export CUDA_VISIBLE_DEVICES=0,1
ollama serve
```

### Memory Limits

```bash
# Limit GPU memory usage (in MB)
export OLLAMA_GPU_MEMORY_FRACTION=0.8
ollama serve
```

## Hermes Integration

### Configuration File

Edit `~/.hermes/config.yaml`:

```yaml
ollama:
  api_base: http://localhost:11434/api/chat  # API endpoint
  model: gpt-oss:20b                         # Model to use
  retry: 3                                    # Retry attempts
  timeout_sec: 180                            # Request timeout (seconds)
```

### Runtime Overrides

```bash
# Use different model
hermes run --prompt "..." --model llama2:13b

# Increase timeout for slow models
hermes run --prompt "..." --timeout 300

# Different API endpoint
hermes run --prompt "..." --api http://remote-host:11434/api/chat
```

## Verification

### Check Server Status

```bash
# Method 1: curl
curl http://localhost:11434/api/version

# Method 2: Test generation
ollama run gpt-oss:20b "Hello, world!"
```

### Test with Hermes

```bash
# Simple test task
hermes run --prompt "テスト" --min-validation 1 --max-validation 1
```

If successful, a report will be generated in `~/.hermes/history/`.

## Troubleshooting

### Server Not Starting

**Symptom**: `ollama serve` fails or exits immediately

**Causes and Solutions**:

1. **Port already in use**
   ```bash
   # Check what's using port 11434
   lsof -i :11434
   sudo netstat -tulpn | grep 11434

   # Kill existing process
   kill <PID>

   # Or use different port
   export OLLAMA_HOST=localhost:11435
   ollama serve
   ```

2. **Permission issues**
   ```bash
   # Check Ollama installation
   which ollama
   ls -la $(which ollama)

   # Reinstall if needed
   curl -fsSL https://ollama.ai/install.sh | sh
   ```

3. **Missing dependencies (Linux)**
   ```bash
   # Install required libraries
   sudo apt-get update
   sudo apt-get install -y libgomp1
   ```

### Connection Refused

**Symptom**: `hermes run` reports "Ollama connection error"

**Solution**:

```bash
# 1. Verify server is running
ps aux | grep ollama
curl http://localhost:11434/api/version

# 2. Start server if not running
ollama serve &

# 3. Check firewall (Linux)
sudo ufw status
sudo ufw allow 11434/tcp

# 4. Verify config
cat ~/.hermes/config.yaml | grep -A 4 ollama
```

### Timeout Errors

**Symptom**: "Request timed out after 180s"

**Causes**:

- Model is too large for available resources
- Complex query requiring long inference time
- GPU memory exhausted

**Solutions**:

1. **Increase timeout**
   ```yaml
   # ~/.hermes/config.yaml
   ollama:
     timeout_sec: 300  # 5 minutes
   ```

2. **Use smaller model**
   ```bash
   hermes run --prompt "..." --model llama2:7b
   ```

3. **Reduce query complexity**
   ```bash
   # Fewer sources and validation loops
   hermes run --prompt "..." \
     --max-search 5 \
     --min-validation 1 \
     --max-validation 2
   ```

4. **Free GPU memory**
   ```bash
   # Kill other GPU processes
   nvidia-smi
   kill <PID>

   # Restart Ollama
   pkill ollama
   ollama serve &
   ```

### Model Not Found (404 Error)

**Symptom**: "Model 'gpt-oss:20b' not found"

**Solution**:

```bash
# List available models
ollama list

# Pull the model
ollama pull gpt-oss:20b

# Verify
ollama list | grep gpt-oss
```

### Slow Performance

**Symptom**: Tasks take 5+ minutes

**Optimization**:

1. **Use GPU if available**
   ```bash
   # Check GPU detection
   nvidia-smi

   # Verify Ollama sees GPU
   ollama run gpt-oss:20b "test"
   # Should show GPU usage in nvidia-smi
   ```

2. **Reduce model size**
   ```bash
   # Smaller models are faster
   hermes run --prompt "..." --model mistral:7b
   ```

3. **Quantized models**
   ```bash
   # Pull quantized version (if available)
   ollama pull gpt-oss:20b-q4_0  # 4-bit quantization
   ```

4. **Increase system resources**
   - Close other applications
   - Increase swap space
   - Add more RAM

### GPU Out of Memory

**Symptom**: CUDA out of memory errors in logs

**Solutions**:

1. **Use CPU mode**
   ```bash
   export CUDA_VISIBLE_DEVICES=""
   pkill ollama
   ollama serve &
   ```

2. **Use smaller model**
   ```bash
   ollama pull llama2:7b
   hermes run --prompt "..." --model llama2:7b
   ```

3. **Reduce batch size** (if available in future Ollama versions)

4. **Close other GPU applications**
   ```bash
   # Check GPU usage
   nvidia-smi

   # Kill GPU processes
   kill <PID>
   ```

### Incorrect Responses

**Symptom**: Generated text is gibberish or repetitive

**Causes**:

- Corrupted model download
- Insufficient system resources
- Model incompatible with Ollama version

**Solutions**:

1. **Re-download model**
   ```bash
   ollama rm gpt-oss:20b
   ollama pull gpt-oss:20b
   ```

2. **Update Ollama**
   ```bash
   curl -fsSL https://ollama.ai/install.sh | sh
   ```

3. **Try different model**
   ```bash
   ollama pull llama2:13b
   hermes run --prompt "..." --model llama2:13b
   ```

## Performance Tuning

### Optimal Settings for Common Hardware

#### 8 GB RAM, No GPU

```yaml
ollama:
  model: mistral:7b
  timeout_sec: 300

validation:
  max_loops: 2

search:
  max_sources: 5
```

#### 16 GB RAM, No GPU

```yaml
ollama:
  model: llama2:13b
  timeout_sec: 240

validation:
  max_loops: 3

search:
  max_sources: 8
```

#### 32+ GB RAM, GPU 8+ GB

```yaml
ollama:
  model: gpt-oss:20b
  timeout_sec: 180

validation:
  max_loops: 3

search:
  max_sources: 12
```

### Batch Processing Optimization

For `hermes queue --all`:

1. **Lower validation loops**
   ```yaml
   validation:
     min_loops: 1
     max_loops: 2
   ```

2. **Limit sources**
   ```yaml
   search:
     max_sources: 6
   ```

3. **Run overnight**
   ```bash
   # Cron job at 2 AM
   0 2 * * * /path/to/venv/bin/hermes queue --all
   ```

## Monitoring

### Check Resource Usage

```bash
# CPU/Memory
top -p $(pgrep ollama)
htop -p $(pgrep ollama)

# GPU
watch -n 1 nvidia-smi

# Disk I/O
iotop -p $(pgrep ollama)
```

### Log Monitoring

```bash
# Ollama logs (if systemd)
journalctl -u ollama -f

# Hermes logs
hermes log --follow
hermes debug --follow
```

### Performance Metrics

Track in Hermes logs:

```bash
# Average response time
hermes debug -n 1000 | grep "Received response" | grep -oE '[0-9.]+s' | awk '{sum+=$1; count++} END {print sum/count "s avg"}'

# Timeout count
hermes debug --error -n 1000 | grep -i timeout | wc -l
```

## Advanced Configuration

### Model Selection Strategy

| Use Case | Recommended Model | RAM Required | Speed |
|----------|------------------|--------------|-------|
| Quick tests | mistral:7b | 8 GB | Fast |
| Balanced quality | llama2:13b | 16 GB | Medium |
| High quality | gpt-oss:20b | 32 GB | Slow |
| Maximum quality | llama2:70b | 64 GB | Very slow |

### Multi-Model Setup

Use different models for different tasks:

```bash
# Fast model for queries
hermes run --prompt "..." --query-model mistral:7b

# Larger model for drafts
hermes run --prompt "..." --draft-model gpt-oss:20b
```

(Note: Multi-model support would require code changes)

## Security Considerations

### Network Exposure

By default, Ollama binds to localhost only. To expose to network:

```bash
# ⚠️ Security risk - use firewall
export OLLAMA_HOST=0.0.0.0:11434
ollama serve
```

**Recommended**: Use reverse proxy with authentication:

```nginx
# nginx config
location /ollama/ {
    auth_basic "Ollama API";
    auth_basic_user_file /etc/nginx/.htpasswd;
    proxy_pass http://localhost:11434/;
}
```

### Model Integrity

Verify model checksums after download:

```bash
# List models with details
ollama list

# Re-download if suspicious
ollama rm gpt-oss:20b
ollama pull gpt-oss:20b
```

## Updating Ollama

```bash
# Linux
curl -fsSL https://ollama.ai/install.sh | sh

# macOS
brew upgrade ollama

# Restart server
pkill ollama
ollama serve &

# Re-test with Hermes
hermes run --prompt "test" --max-validation 1
```

## Uninstallation

### Remove Ollama

```bash
# Linux
sudo rm /usr/local/bin/ollama
sudo rm -rf /usr/share/ollama

# macOS
brew uninstall ollama

# Remove models and data
rm -rf ~/.ollama
```

### Remove Hermes Configuration

```bash
# Keep history but reset Ollama config
hermes run --clear
```

## Related Documentation

- [Hermes Configuration](../../README.md#configuration-overview)
- [hermes run Command](../command/run.md)
- [Troubleshooting Guide](../../README.md#troubleshooting-highlights)
- [Official Ollama Docs](https://github.com/ollama/ollama)

## Support

- **Ollama Issues**: https://github.com/ollama/ollama/issues
- **Hermes Issues**: Check `hermes debug --error` for diagnostics
