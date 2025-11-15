# Troubleshooting

This guide summarizes common problems that may occur while using Hermes and their solutions.

## 1. Cannot connect to Ollama

If you see an error related to Ollama (e.g., `Connection refused`) when running `hermes run`.

### Cause

-   The Ollama service is not running.
-   The `api_url` in `config.yaml` is incorrect.
-   The connection is blocked by a firewall.

### Solution

1.  **Check Ollama's status**:
    First, check if the Ollama server is running properly. Run the following command in the terminal to see if a list of installed models is returned.

    ```bash
    curl http://localhost:11434/api/tags
    ```

    If an error is returned, Ollama may not be running.

2.  **Restart the Ollama service**:
    Restart the Ollama service with the following command.

    ```bash
    # If using systemd
    sudo systemctl restart ollama

    # Or, simply start it directly in the terminal
    ollama serve
    ```

3.  **Check the configuration file**:
    Open `~/.hermes/config.yaml` and check if `ollama.api_url` is correct. The default is `http://localhost:11434/api/chat`.

## 2. Cannot connect to SearxNG / Cannot retrieve search results

If an error occurs during the web search step.

### Cause

-   The SearxNG Docker container is not running.
-   The Redis Docker container is not running.
-   Network problems or firewall.
-   There is a problem with the SearxNG configuration itself.

### Solution

1.  **Check the status of the Docker containers**:
    Navigate to the Hermes workspace directory and run `docker compose ps` to confirm that both the `searxng` and `redis` containers are in the `Up` (or `running`) state.

    ```bash
    cd ~/.hermes
    docker compose ps
    ```

2.  **Check the container logs**:
    If either container is not `Up`, or if the problem persists, check the logs for detailed error messages.

    ```bash
    # Check SearxNG logs
    docker compose logs searxng

    # Check Redis logs
    docker compose logs redis
    ```

3.  **Restart the services**:
    Restarting the containers may solve the problem.

    ```bash
    docker compose restart
    ```

4.  **Check the SearxNG configuration**:
    Check the `~/.hermes/searxng/settings.yml` file to ensure that the search engine settings are enabled. A specific search engine may be blocked.

5.  **Check the firewall settings**:
    Make sure that the firewall is not preventing the Docker containers from accessing the external network.

## 3. How to check logs

For more detailed troubleshooting, it is useful to check the logs of Hermes itself.

-   **Normal logs**:
    You can check the main logs with the `hermes log` command.

    ```bash
    hermes log --lines 200
    ```

-   **Debug logs**:
    By adding the `--debug` flag, you can check more detailed logs, such as the thought process of each step of the agent and API responses. This is very useful for isolating problems.

    ```bash
    hermes log --debug --lines 500
    ```

-   **Real-time logs**:
    By adding the `--follow` flag, you can track the logs of the currently running task in real-time.

    ```bash
    hermes log --follow --debug
    ```
