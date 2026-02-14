# Universal MCP Server Configuration for Cursor/Windsurf

# For Cursor:
# 1. Open Cursor Settings (Cmd/Ctrl + ,)
# 2. Navigate to Features > MCP Servers
# 3. Add a new server with the following configuration:

{
  "mcpServers": {
    "universal-mcp": {
      "command": "python",
      "args": ["/home/slave/Desktop/tuiTest/mcp-server-demo/src/server.py"],
      "env": {
        "MYSQL_HOST": "${MYSQL_HOST}",
        "MYSQL_PORT": "${MYSQL_PORT}",
        "MYSQL_USER": "${MYSQL_USER}",
        "MYSQL_PASSWORD": "${MYSQL_PASSWORD}",
        "MYSQL_DATABASE": "${MYSQL_DATABASE}",
        "POSTGRES_HOST": "${POSTGRES_HOST}",
        "POSTGRES_PORT": "${POSTGRES_PORT}",
        "POSTGRES_USER": "${POSTGRES_USER}",
        "POSTGRES_PASSWORD": "${POSTGRES_PASSWORD}",
        "POSTGRES_DATABASE": "${POSTGRES_DATABASE}",
        "MONGO_HOST": "${MONGO_HOST}",
        "MONGO_PORT": "${MONGO_PORT}",
        "MONGO_DATABASE": "${MONGO_DATABASE}",
        "GITHUB_TOKEN": "${GITHUB_TOKEN}",
        "GITHUB_OWNER": "${GITHUB_OWNER}",
        "GITHUB_REPO": "${GITHUB_REPO}",
        "CUSTOM_API_URL": "${CUSTOM_API_URL}",
        "CUSTOM_API_KEY": "${CUSTOM_API_KEY}",
        "CUSTOM_API_HEADERS": "${CUSTOM_API_HEADERS}"
      }
    }
  }
}

# Note: Environment variables should be set in your system shell or
# you can hardcode values (not recommended for sensitive data)
