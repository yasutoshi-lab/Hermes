# Browser-use Integration

## Overview

Browser-use is an optional web automation library that enhances Hermes' web research capabilities. Hermes works out-of-the-box with DuckDuckGo fallback and automatically upgrades to browser-use when available.

## Operational Modes

Hermes supports two web research modes:

### Mode 1: DuckDuckGo Fallback (Default)

- **Enabled**: Out-of-the-box, no setup required
- **Technology**: `duckduckgo-search` + `httpx`
- **Capabilities**:
  - Text search via DuckDuckGo
  - HTTP content fetching
  - Basic HTML parsing
  - robots.txt respect
- **Limitations**:
  - No JavaScript rendering
  - No interactive elements
  - Subject to rate limiting
  - Basic content extraction

### Mode 2: browser-use (Enhanced)

- **Enabled**: When `browser-use` package installed
- **Technology**: Playwright + browser automation
- **Capabilities**:
  - Full JavaScript rendering
  - Interactive element handling
  - Advanced page scraping
  - Dynamic content support
- **Requirements**:
  - Source installation (not yet on PyPI)
  - Playwright browser binaries
  - Additional disk space (~300 MB)

## When to Use Each Mode

### Use DuckDuckGo Mode (Default) When:

- Getting started with Hermes
- Researching text-heavy topics
- Network bandwidth is limited
- Disk space is constrained
- Simple content extraction suffices
- Rate limiting is not an issue

### Use browser-use Mode When:

- Need JavaScript-rendered content
- Scraping single-page applications (SPAs)
- Interacting with dynamic web pages
- Requiring precise element selection
- Need screenshot capabilities
- Advanced automation features required

## Installation

### Prerequisites

- Python 3.10+
- Hermes already installed
- Internet connection
- 500 MB free disk space

### Install browser-use from Source

Currently, browser-use is not available on PyPI. Install from GitHub:

```bash
# Navigate to temporary directory
cd /tmp

# Clone repository
git clone https://github.com/browser-use/browser-use.git
cd browser-use

# Install package
pip install -e .

# Verify installation
python -c "import browser_use; print('browser-use installed')"
```

### Install Playwright Browsers

browser-use uses Playwright for browser automation:

```bash
# Install Chromium browser
playwright install chromium

# Install system dependencies (Linux only)
playwright install-deps chromium

# Verify installation
playwright --version
```

### Install Hermes browser Extra

After browser-use is installed:

```bash
cd /path/to/Hermes
pip install -e .[browser]
```

This ensures all browser-related dependencies are present.

## Configuration

### Automatic Detection

Hermes automatically detects browser-use:

```python
# Hermes checks on startup
try:
    from browser_use import BrowserAgent
    # Uses browser-use if available
except ImportError:
    # Falls back to DuckDuckGo
    pass
```

No configuration changes needed!

### Verify Detection

```bash
# Run a test task
hermes run --prompt "test browser" --max-validation 1

# Check logs for detection message
hermes log -n 50 | grep browser

# Expected: "browser-use detected; BrowserAgent initialized"
# or: "Using DuckDuckGo fallback"
```

### Force DuckDuckGo Mode

To disable browser-use temporarily:

```bash
# Uninstall browser-use
pip uninstall browser-use

# Or rename import (temporary)
python -c "import sys; sys.modules['browser_use'] = None"
```

## Verification

### Test DuckDuckGo Mode

```bash
# Ensure browser-use is not installed
pip list | grep browser-use

# Run test
python tests/test_browser_client.py
```

**Expected output**:
```
Sample result: Example Title -> https://example.com
Snippet: Brief description...
Content preview: Full text...
Fetched 2 total sources.
```

### Test browser-use Mode

```bash
# Ensure browser-use is installed
python -c "import browser_use; print('OK')"

# Run test task
hermes run --prompt "JavaScript framework comparison" --max-validation 1

# Check logs
hermes log -n 20 | grep -i browser
```

Expected log line:
```
[INFO] [WEB] browser-use detected; BrowserAgent initialized.
```

## Troubleshooting

### browser-use Not Detected

**Symptom**: Logs show "Using DuckDuckGo fallback" even after installation

**Solutions**:

1. **Verify installation**
   ```bash
   python -c "import browser_use; print(browser_use.__version__)"
   ```

2. **Check virtual environment**
   ```bash
   which python
   pip list | grep browser-use
   ```

3. **Reinstall**
   ```bash
   pip uninstall browser-use
   cd /tmp/browser-use
   pip install -e .
   ```

4. **Check import errors**
   ```bash
   python -c "from browser_use import BrowserAgent; print('OK')"
   ```

### Playwright Installation Failed

**Symptom**: `playwright install` fails with errors

**Linux Solutions**:

```bash
# Update system packages
sudo apt-get update
sudo apt-get upgrade

# Install missing dependencies
sudo apt-get install -y \
    libnss3 \
    libnspr4 \
    libatk1.0-0 \
    libatk-bridge2.0-0 \
    libcups2 \
    libdrm2 \
    libxkbcommon0 \
    libxcomposite1 \
    libxdamage1 \
    libxfixes3 \
    libxrandr2 \
    libgbm1 \
    libpango-1.0-0 \
    libcairo2 \
    libasound2

# Retry Playwright installation
playwright install chromium
playwright install-deps chromium
```

**macOS Solutions**:

```bash
# Ensure Xcode Command Line Tools installed
xcode-select --install

# Retry installation
playwright install chromium
```

**Permission Issues**:

```bash
# Run with sudo (not recommended)
sudo playwright install chromium

# Or fix permissions
sudo chown -R $USER:$USER ~/.cache/ms-playwright
playwright install chromium
```

### Browser Launch Failures

**Symptom**: "Failed to launch browser" errors

**Causes and Solutions**:

1. **Missing executable**
   ```bash
   # Check Playwright browsers
   ls ~/.cache/ms-playwright/

   # Reinstall if missing
   playwright install chromium
   ```

2. **Display server issues (Linux)**
   ```bash
   # Set headless mode (already default in Hermes)
   export PLAYWRIGHT_BROWSERS_PATH=0

   # Or use Xvfb
   sudo apt-get install xvfb
   xvfb-run hermes run --prompt "test"
   ```

3. **Insufficient memory**
   ```bash
   # Check available RAM
   free -h

   # Close other applications
   # Or increase swap space
   ```

### Slow Performance

**Symptom**: Tasks take significantly longer with browser-use

**Causes**:

- Browser startup overhead (~2-5 seconds per query)
- JavaScript rendering time
- Network latency

**Optimization**:

1. **Reduce source count**
   ```bash
   hermes run --prompt "..." --max-search 5
   ```

2. **Use DuckDuckGo for simple queries**
   ```bash
   pip uninstall browser-use  # Temporary
   hermes run --prompt "..."
   pip install -e /tmp/browser-use  # Restore
   ```

3. **Batch queries**
   ```bash
   # Schedule multiple tasks
   hermes task --prompt "Topic 1"
   hermes task --prompt "Topic 2"

   # Run overnight
   hermes queue --all
   ```

### Rate Limiting

**Symptom**: DuckDuckGo returns 429 errors or empty results

**Applies to**: Both modes (browser-use also uses search engines)

**Solutions**:

1. **Add delays between runs**
   ```bash
   hermes run --prompt "Query 1"
   sleep 60
   hermes run --prompt "Query 2"
   ```

2. **Reduce sources**
   ```bash
   hermes run --prompt "..." --max-search 3
   ```

3. **Use different search engine** (requires code modification)

4. **Wait and retry**
   ```bash
   # Wait 2-5 minutes
   sleep 120
   hermes run --prompt "..."
   ```

### robots.txt Blocking

**Symptom**: "Robots.txt disallows fetching" in logs

**Behavior**: Hermes respects robots.txt by default

**Solutions**:

1. **Rely on snippet/summary** (no change needed)

2. **Manual intervention** (if critical)
   ```bash
   # Extract URL from logs
   hermes debug -n 100 | grep "disallows fetching"

   # Manually visit and save content
   curl https://example.com > content.txt
   ```

3. **Focus on sources that allow scraping**
   - Academic sites (arxiv.org, scholar.google.com)
   - News sites (typically allow)
   - Open data platforms

### Memory Leaks

**Symptom**: RAM usage grows over time

**Cause**: Browser instances not properly cleaned up

**Solution**:

```bash
# Kill orphaned Chrome processes
pkill -f chrome
pkill -f chromium

# Restart Hermes task
hermes run --prompt "..."
```

**Prevention** (already implemented in Hermes):

- Context manager usage (`with BrowserUseClient()`)
- Explicit cleanup in error handlers

## Advanced Configuration

### Browser-use Settings

Currently, browser-use settings are hardcoded in `BrowserUseClient`. Future versions may support:

```yaml
# Future ~/.hermes/config.yaml
browser:
  headless: true
  timeout: 30
  user_agent: "Mozilla/5.0 ..."
  viewport_width: 1920
  viewport_height: 1080
```

### Custom User Agent

Edit `hermes_cli/tools/browser_use_client.py`:

```python
USER_AGENT = "Mozilla/5.0 (compatible; HermesBot/1.0)"
```

### Proxy Configuration

For network restrictions:

```bash
# Set environment variables
export HTTP_PROXY=http://proxy.example.com:8080
export HTTPS_PROXY=http://proxy.example.com:8080

# Run Hermes
hermes run --prompt "..."
```

## Performance Comparison

### Benchmark: Simple Text Query

| Mode | Source Count | Time | Quality |
|------|-------------|------|---------|
| DuckDuckGo | 8 | 15s | Good |
| browser-use | 8 | 45s | Excellent |

### Benchmark: JavaScript-heavy Sites

| Mode | Source Count | Time | Quality |
|------|-------------|------|---------|
| DuckDuckGo | 8 | 20s | Poor (missing content) |
| browser-use | 8 | 60s | Excellent |

### Recommendation

- **Default**: Use DuckDuckGo (faster, sufficient for most cases)
- **When needed**: Install browser-use for specialized tasks
- **Production**: Test both modes for your specific use case

## Switching Between Modes

### Temporary Switch

```bash
# Disable browser-use for one run
pip uninstall browser-use -y
hermes run --prompt "..."

# Re-enable
cd /tmp/browser-use && pip install -e .
```

### Permanent Switch

**To DuckDuckGo only**:
```bash
pip uninstall browser-use
```

**To browser-use**:
```bash
# Ensure installed
cd /tmp/browser-use && pip install -e .
```

## Testing

### Unit Tests

```bash
# Test DuckDuckGo mode
pytest tests/test_browser_client.py

# Test with browser-use (if installed)
# Same test auto-detects browser-use
python -c "import browser_use" && pytest tests/test_browser_client.py
```

### Integration Test

```bash
# Full workflow test
hermes run --prompt "Compare Python web frameworks" \
  --max-validation 1 \
  --max-search 5

# Check which mode was used
hermes log -n 50 | grep -i browser
```

## Disk Space Management

### Check Usage

```bash
# Playwright browsers
du -sh ~/.cache/ms-playwright/

# browser-use package
du -sh /tmp/browser-use/
```

### Clean Up

```bash
# Remove Playwright browsers
playwright uninstall

# Remove browser-use
pip uninstall browser-use
rm -rf /tmp/browser-use
```

### Minimal Setup

For constrained environments:

```bash
# Use DuckDuckGo only (no browser-use)
pip install -e .  # Hermes base install only
```

## Security Considerations

### Headless Mode

Hermes runs browsers in headless mode (no GUI) by default for security.

### Sandboxing

Playwright browsers run in sandboxed mode. To disable (not recommended):

```bash
export PLAYWRIGHT_CHROMIUM_ARGS="--no-sandbox"
hermes run --prompt "..."
```

### Data Privacy

- Browser-use may cache data in `~/.cache/ms-playwright/`
- Clear cache periodically:
  ```bash
  rm -rf ~/.cache/ms-playwright/
  playwright install chromium
  ```

## Future Enhancements

Planned features for browser-use integration:

- Configurable browser settings in `config.yaml`
- Screenshot capture for visual analysis
- Cookie/session management
- Multi-browser support (Firefox, Safari)
- Distributed browser pool

## Related Documentation

- [Container-use Integration](./container-use.md)
- [Ollama Integration](./ollama.md)
- [Hermes Architecture](../../ARCHITECTURE.md)
- [Troubleshooting](../../README.md#troubleshooting-highlights)

## External Resources

- [browser-use GitHub](https://github.com/browser-use/browser-use)
- [Playwright Documentation](https://playwright.dev/)
- [DuckDuckGo Search API](https://duckduckgo.com/api)

## Support

For browser-use specific issues:
- Check `hermes debug --error` for error traces
- Verify Playwright installation: `playwright --version`
- Test browser launch: `playwright open chromium`
- Report issues with logs from `hermes debug -n 200`
