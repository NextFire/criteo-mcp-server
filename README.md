# criteo-mcp-server

**Prerequisites:**

- [`uv`](https://github.com/astral-sh/uv)
- a client credentials application

```sh
./generate-client.sh <retailmedia|marketingsolutions> <version>
CRITEO_MCP_CLIENT_ID=<client_id> CRITEO_MCP_CLIENT_SECRET=<client_secret> uv run criteo-mcp-server
```

You can also set `CRITEO_MCP_BASE_URL` to customize the path to the API server (defaults to https://api.criteo.com).

## Claude Desktop config

```json
{
  "mcpServers": {
    "Criteo API": {
      "command": "uv",
      "args": ["run", "--directory", "<project_dir>", "criteo-mcp-server"],
      "env": {
        "CRITEO_MCP_CLIENT_ID": "<client_id>",
        "CRITEO_MCP_CLIENT_SECRET": "<client_secret>"
      }
    }
  }
}
```

## Visual Studio Code config

For GitHub Copilot agent mode: `.vscode/mcp.json`

```json
{
  "servers": {
    "Criteo API": {
      "type": "stdio",
      "command": "uv",
      "args": ["run", "--directory", "${workspaceFolder}", "criteo-mcp-server"],
      "env": {
        "CRITEO_MCP_CLIENT_ID": "<client_id>",
        "CRITEO_MCP_CLIENT_SECRET": "<client_secret>"
      }
    }
  }
}
```
