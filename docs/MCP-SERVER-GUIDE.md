# Universal MCP Server - Complete Guide

A comprehensive tutorial on building and using Model Context Protocol (MCP) servers in 2026.

---

## Table of Contents

1. [Introduction to MCP](#introduction-to-mcp)
2. [What is MCP?](#what-is-mcp)
3. [MCP Architecture](#mcp-architecture)
4. [Server Features](#server-features)
5. [Installation](#installation)
6. [Configuration](#configuration)
7. [Using with Claude Desktop](#using-with-claude-desktop)
8. [Using with Claude Code](#using-with-claude-code)
9. [Using with Cursor/Windsurf](#using-with-cursorwindsurf)
10. [Tool Reference](#tool-reference)
11. [Best Practices](#best-practices)
12. [Security Considerations](#security-considerations)
13. [Troubleshooting](#troubleshooting)
14. [Extending the Server](#extending-the-server)

---

## Introduction to MCP

The Model Context Protocol (MCP) is an open standard developed by Anthropic that enables AI assistants to connect to external tools, data sources, and services through a unified interface. Think of it as "USB-C for AI" - a standardized way to connect AI models to the tools and data they need.

As of 2026, the MCP ecosystem has grown significantly:
- **3,000+ servers** indexed on MCP.so
- **2,200+ servers** on Smithery
- **Linux Foundation governance** after Anthropic donated MCP to the Agentic AI Foundation

---

## What is MCP?

MCP standardizes how AI models communicate with external systems through three core primitives:

### 1. Tools
Functions the AI model can call to perform actions:
- Query databases
- Create issues
- Send emails
- Read/write files
- Call APIs

### 2. Resources
Data the AI model can read:
- Files
- Database records
- API responses
- Configuration data

### 3. Prompts
Reusable templates that guide model behavior for specific tasks.

---

## MCP Architecture

```
┌─────────────────┐      MCP       ┌─────────────────┐
│   AI Assistant  │◄──────────────►│   MCP Server    │
│  (Claude, etc.) │                │  (Your Server)  │
└─────────────────┘                └────────┬────────┘
                                            │
                    ┌───────────────────────┼───────────────────────┐
                    │                       │                       │
                    ▼                       ▼                       ▼
              ┌──────────┐          ┌──────────┐          ┌──────────┐
              │  GitHub  │          │Databases │          │ Filesytem│
              └──────────┘          └──────────┘          └──────────┘
```

**Components:**
- **MCP Host**: The AI application (Claude Desktop, Claude Code, Cursor)
- **MCP Client**: Protocol-level client inside the host
- **MCP Server**: Your code exposing tools, resources, and prompts

---

## Server Features

This universal MCP server provides:

### GitHub Integration
- List and get issues
- Create new issues
- List pull requests
- Read repository files

### Database Support
- **MySQL**: Execute queries, list tables, describe schemas
- **PostgreSQL**: Execute queries, list tables, describe schemas
- **MongoDB**: Find documents, run aggregations, count documents

### Filesystem Operations
- Read/write files
- List directories
- Create directories
- Delete files
- Search with glob patterns

### Custom API
- GET, POST, PUT, DELETE requests
- Custom headers and authentication
- Parameter support

### Local Git
- List repositories and branches
- View commit history and details
- Stage and commit changes
- Push/pull from remotes
- Clone repositories

**Quick Start:** Local git operations work out of the box! Just set `LOCAL_GIT_BASE_PATH` in your config - no database credentials needed.

---

## Installation

### Prerequisites
- Python 3.10 or higher
- pip or poetry for package management

### Step 1: Clone or Download the Server

```bash
cd /home/slave/Desktop/tuiTest
# If using git (optional):
# git clone <repository-url> mcp-server-demo
```

### Step 2: Create Virtual Environment

```bash
cd mcp-server-demo
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

**Important:** Use the venv Python, not system Python:
```bash
# Verify correct Python
which python  # Should show: /path/to/mcp-server-demo/venv/bin/python
```

### Step 3: Install Dependencies

```bash
pip install -e .
```

Or install individually:

```bash
pip install fastmcp pymysql pymongo psycopg2-binary sqlalchemy pydantic httpx python-dotenv pygithub aiofiles
```

### Step 4: Configure Environment

```bash
cp config/.env.example config/.env
# Edit config/.env with your actual values
```

**Note:** For local git operations, you only need to set `LOCAL_GIT_BASE_PATH`:

```bash
# Minimum config for local git repos (no database credentials needed)
LOCAL_GIT_BASE_PATH=/home/slave/Desktop/tuiTest
LOCAL_GIT_DEFAULT_BRANCH=main
```

For other integrations, configure the relevant environment variables in `.env`.

---

## Configuration

### Environment Variables

#### GitHub Configuration

| Variable | Description | Example |
|----------|-------------|---------|
| `GITHUB_TOKEN` | Personal Access Token | `ghp_xxxxxxxxxxxx` |
| `GITHUB_OWNER` | GitHub username or organization | `octocat` |
| `GITHUB_REPO` | Repository name | `hello-world` |

**Creating a GitHub Token:**
1. Go to https://github.com/settings/tokens
2. Click "Generate new token (classic)"
3. Select scopes: `repo` (full control)
4. Copy the generated token

#### MySQL Configuration

| Variable | Description | Default |
|----------|-------------|---------|
| `MYSQL_HOST` | Database host | `localhost` |
| `MYSQL_PORT` | Database port | `3306` |
| `MYSQL_USER` | Database user | `root` |
| `MYSQL_PASSWORD` | Database password | (empty) |
| `MYSQL_DATABASE` | Database name | `test` |

#### PostgreSQL Configuration

| Variable | Description | Default |
|----------|-------------|---------|
| `POSTGRES_HOST` | Database host | `localhost` |
| `POSTGRES_PORT` | Database port | `5432` |
| `POSTGRES_USER` | Database user | `postgres` |
| `POSTGRES_PASSWORD` | Database password | (empty) |
| `POSTGRES_DATABASE` | Database name | `test` |

#### MongoDB Configuration

| Variable | Description | Default |
|----------|-------------|---------|
| `MONGO_HOST` | MongoDB host | `localhost` |
| `MONGO_PORT` | MongoDB port | `27017` |
| `MONGO_DATABASE` | Database name | `test` |

#### Custom API Configuration

| Variable | Description | Example |
|----------|-------------|---------|
| `CUSTOM_API_URL` | Base URL of the API | `https://api.example.com` |
| `CUSTOM_API_KEY` | API key for authentication | `your-api-key` |
| `CUSTOM_API_HEADERS` | Additional headers as JSON | `{"X-Custom": "value"}` |

#### Local Git Configuration

| Variable | Description | Example |
|----------|-------------|---------|
| `LOCAL_GIT_BASE_PATH` | Base directory containing git repos | `/home/slave/Desktop/tuiTest` |
| `LOCAL_GIT_DEFAULT_BRANCH` | Default branch name | `main` |

### Loading Environment Variables

The server automatically loads from `.env` file if present in the same directory:

```bash
# Set environment variables before running
export GITHUB_TOKEN="your-token"
export MYSQL_DATABASE="mydb"
python src/server.py
```

---

## Using with Claude Desktop

### Step 1: Locate Configuration Directory

- **macOS**: `~/Library/Application Support/Claude/`
- **Windows**: `%APPDATA%/Claude/`
- **Linux**: `~/.config/Claude/`

### Step 2: Edit Configuration

Open or create `claude_desktop_config.json` in the configuration directory:

```json
{
  "mcpServers": {
    "universal-mcp": {
      "command": "python",
      "args": ["/home/slave/Desktop/tuiTest/mcp-server-demo/src/server.py"],
      "env": {
        "GITHUB_TOKEN": "your-github-token",
        "GITHUB_OWNER": "your-username",
        "GITHUB_REPO": "your-repo",
        "MYSQL_DATABASE": "your-db"
      }
    }
  }
}
```

### Step 3: Restart Claude Desktop

Close and reopen Claude Desktop. The server should automatically connect.

### Step 4: Verify Connection

In Claude Desktop, you can now use commands like:

```
Show me the issues in my GitHub repository
List all tables in my MySQL database
Read the file /path/to/file.txt
```

---

## Using with Claude Code

### Step 1: Locate Configuration Directory

- **macOS/Linux**: `~/.claude/`
- **Windows**: `%USERPROFILE%/.claude/`

### Step 2: Edit Configuration

Open or create `.mcp.json` in the configuration directory:

```json
{
  "mcpServers": {
    "universal-mcp": {
      "command": "python",
      "args": ["/home/slave/Desktop/tuiTest/mcp-server-demo/src/server.py"],
      "env": {
        "GITHUB_TOKEN": "your-github-token",
        "GITHUB_OWNER": "your-username",
        "GITHUB_REPO": "your-repo"
      }
    }
  }
}
```

### Step 3: Restart Claude Code

Exit and restart your terminal or Claude Code session.

### Step 4: Tool Search (2026 Feature)

Claude Code 2.1.7+ includes **Tool Search** with lazy loading:
- Tools are loaded on-demand, not all at session start
- Reduces context window usage
- Enabled by default

---

## Using with Cursor/Windsurf

### Cursor Setup

1. Open Cursor Settings (`Cmd/Ctrl + ,`)
2. Navigate to **Features** → **MCP Servers**
3. Click **Add new MCP server**
4. Configure:

```json
{
  "name": "universal-mcp",
  "command": "python",
  "args": ["/home/slave/Desktop/tuiTest/mcp-server-demo/src/server.py"],
  "env": {
    "GITHUB_TOKEN": "your-token"
  }
}
```

### Windsurf Setup

Similar to Cursor:
1. Open Settings → **Advanced** → **MCP Servers**
2. Add the same configuration

---

## Tool Reference

### GitHub Tools

| Tool | Description | Parameters |
|------|-------------|-------------|
| `github_list_issues` | List repository issues | `state` (open/closed/all), `limit` |
| `github_get_issue` | Get specific issue | `issue_number` |
| `github_create_issue` | Create new issue | `title`, `body`, `labels` |
| `github_list_pulls` | List pull requests | `state` |
| `github_get_file_content` | Read file from repo | `path`, `ref` |

### MySQL Tools

| Tool | Description | Parameters |
|------|-------------|-------------|
| `mysql_execute_query` | Execute SELECT query | `query`, `params` |
| `mysql_list_tables` | List all tables | (none) |
| `mysql_describe_table` | Get table schema | `table_name` |

### PostgreSQL Tools

| Tool | Description | Parameters |
|------|-------------|-------------|
| `postgresql_execute_query` | Execute SELECT query | `query`, `params` |
| `postgresql_list_tables` | List all tables | (none) |
| `postgresql_describe_table` | Get table schema | `table_name` |

### MongoDB Tools

| Tool | Description | Parameters |
|------|-------------|-------------|
| `mongodb_list_collections` | List collections | (none) |
| `mongodb_find` | Find documents | `collection`, `filter`, `limit` |
| `mongodb_aggregate` | Run aggregation | `collection`, `pipeline` |
| `mongodb_count` | Count documents | `collection`, `filter` |

### Filesystem Tools

| Tool | Description | Parameters |
|------|-------------|-------------|
| `filesystem_read_file` | Read file contents | `path` |
| `filesystem_write_file` | Write to file | `path`, `content` |
| `filesystem_list_directory` | List directory | `path`, `pattern` |
| `filesystem_create_directory` | Create directory | `path` |
| `filesystem_delete_file` | Delete file | `path` |
| `filesystem_search` | Search files | `directory`, `pattern` |

### Custom API Tools

| Tool | Description | Parameters |
|------|-------------|-------------|
| `custom_api_get` | GET request | `endpoint`, `params` |
| `custom_api_post` | POST request | `endpoint`, `body` |
| `custom_api_put` | PUT request | `endpoint`, `body` |
| `custom_api_delete` | DELETE request | `endpoint` |

### Local Git Tools

| Tool | Description | Parameters |
|------|-------------|-------------|
| `git_list_repos` | List available local repositories | (none) |
| `git_list_branches` | List branches in repository | `repo_path` |
| `git_get_status` | Get working tree status | `repo_path` |
| `git_get_log` | Get commit history | `repo_path`, `max_count`, `branch` |
| `git_show_commit` | Show commit details | `repo_path`, `sha` |
| `git_list_tags` | List repository tags | `repo_path` |
| `git_get_file_diff` | Get file diff | `repo_path`, `file_path`, `branch` |
| `git_get_current_branch` | Get current branch | `repo_path` |
| `git_checkout_branch` | Checkout a branch | `repo_path`, `branch`, `create` |
| `git_stage_file` | Stage files for commit | `repo_path`, `file_path` |
| `git_commit` | Commit staged changes | `repo_path`, `message` |
| `git_pull` | Pull from remote | `repo_path` |
| `git_push` | Push to remote | `repo_path`, `remote`, `branch` |
| `git_get_remote` | Get remote info | `repo_path` |
| `git_clone` | Clone repository | `source_url`, `target_path` |

---

## Best Practices

### 1. Design for Outcomes, Not Operations

**Bad**: Exposing every API endpoint as a separate tool
- `get_user_by_email()`
- `list_orders(user_id)`
- `get_order_status(order_id)`

**Good**: One high-level tool
- `track_order(email)` - does everything internally

### 2. Curate Ruthlessly

- **5-15 tools per server** maximum
- One server, one job
- Delete unused tools
- Split by persona (admin/user)

### 3. Instructions Are Context

- Write tool descriptions for the AI model
- Include examples of valid inputs
- Describe what the output looks like
- Use clear error messages

### 4. Paginate Large Results

```python
# Always limit results
cursor.limit(20)  # Default to 20-50
```

### 5. Name Tools for Discovery

**Good**:
- `github_create_issue`
- `mysql_execute_query`

**Bad**:
- `create_issue` (too generic)
- `query` (meaningless)

### 6. Handle Errors Gracefully

```python
try:
    # operation
except Exception as e:
    return json.dumps({"error": str(e)})
```

---

## Security Considerations

### 1. Environment Variables

Never hardcode secrets. Use environment variables:

```bash
# Good
export GITHUB_TOKEN="ghp_xxx"

# Bad - don't do this
GITHUB_TOKEN = "ghp_xxx"  # in code
```

### 2. Input Validation

Always validate and sanitize inputs:

```python
# Check for path traversal
file_path = Path(path).resolve()
if not file_path.is_relative_to(allowed_dir):
    raise ValueError("Access denied")
```

### 3. Read-Only Database Queries

For safety, database tools should be read-only:

```python
# Only allow SELECT
if query.strip().upper().startswith("SELECT"):
    cursor.execute(query)
else:
    raise ValueError("Only SELECT queries allowed")
```

### 4. Rate Limiting

Consider adding rate limits for production:

```python
from functools import wraps
import time

def rate_limit(calls=10, period=60):
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            # implementation
            return func(*args, **kwargs)
        return wrapper
    return decorator
```

### 5. Authentication

For remote SSE transport, implement authentication:

```python
from fastmcp.transport import SSETransport
import hmac

def verify_auth(token):
    expected = os.getenv("SERVER_AUTH_TOKEN")
    return hmac.compare_digest(token, expected)

mcp.run(transport=SSETransport(
    host="0.0.0.0",
    port=8080,
    auth=verify_auth
))
```

---

## Troubleshooting

### Server Not Starting

**Error**: `ModuleNotFoundError: No module named 'fastmcp'`

**Solution**:
```bash
cd /home/slave/Desktop/tuiTest/mcp-server-demo
source venv/bin/activate
pip install fastmcp
```

### Working Directory Error

**Error**: Path resolution failures or "directory not found" errors

**Solution**: The server MUST run from the project directory. The client configs include a `bash -c` wrapper to handle this:

```bash
# Config uses this pattern:
"command": "bash", "args": ["-c", "cd /home/slave/Desktop/tuiTest/mcp-server-demo && /path/to/venv/bin/python src/server.py"]
```

If testing manually:
```bash
cd /home/slave/Desktop/tuiTest/mcp-server-demo
source venv/bin/activate
python src/server.py
```

### Claude Desktop Not Connecting

1. Check if server starts manually:
```bash
cd /home/slave/Desktop/tuiTest/mcp-server-demo
source venv/bin/activate
echo '{"jsonrpc":"2.0","method":"initialize","params":{"capabilities":{},"clientInfo":{"name":"test","version":"1.0.0"},"protocolVersion":"2024-11-05"},"id":1}' | python src/server.py
```

2. Check configuration path is correct
3. Verify Python path in config includes full path to venv

### Database Connection Errors

1. Verify database is running:
```bash
mysql -h localhost -u root -p
psql -h localhost -U postgres
mongosh
```

2. Check environment variables are set
3. Verify network connectivity

### GitHub API Errors

1. Verify token is valid: https://github.com/settings/tokens
2. Check token has required scopes
3. Verify owner/repo are correct

### stdout Pollution

**Problem**: Dependencies writing to stdout break JSON-RPC

**Solution**: Ensure all logging goes to stderr:
```python
import sys

# Correct - logs to stderr
print("Server started", file=sys.stderr)

# Wrong - breaks protocol
print("Server started")
```

---

## Extending the Server

### Adding New Tools

```python
@mcp.tool()
async def my_new_tool(param1: str, param2: int = 10) -> str:
    """Description for the AI model.
    
    Args:
        param1: Description of first parameter
        param2: Description of second parameter (default: 10)
    
    Returns:
        JSON string with results
    """
    # Your implementation
    return json.dumps({"result": "success"})
```

### Adding New Resources

```python
@mcp.resource("custom://my-resource")
async def my_resource() -> str:
    """Description of what this resource provides."""
    return json.dumps({"data": "value"})
```

### Adding New Prompts

```python
@mcp.prompt()
def my_prompt() -> str:
    """Instructions for the AI when using this prompt."""
    return """You are helping with...
    
    Guidelines:
    1. Do this
    2. Do that
    """
```

### SSE Transport for Remote Deployment

For remote access, use SSE transport:

```bash
python src/server.py --transport=sse
```

This starts an HTTP server on port 8080.

Client configuration for SSE:
```json
{
  "mcpServers": {
    "universal-mcp": {
      "url": "http://your-server:8080/sse"
    }
  }
}
```

---

## Quick Reference

### Starting the Server (Manual Testing)

The server must run from the project directory for proper path resolution:

```bash
# Navigate to project directory
cd /home/slave/Desktop/tuiTest/mcp-server-demo

# Activate virtual environment
source venv/bin/activate

# Run the server (stdio transport - for AI clients)
python src/server.py

# Or use full path to Python
/home/slave/Desktop/tuiTest/mcp-server-demo/venv/bin/python src/server.py
```

**For SSE/HTTP transport (remote access):**
```bash
cd /home/slave/Desktop/tuiTest/mcp-server-demo
source venv/bin/activate
python src/server.py --transport=sse
# Server runs on http://localhost:8080
```

### Stopping the Server

**Manual testing:**
- Press `Ctrl+C` to stop the server

**When running via AI client (Claude Desktop/Code/Cursor):**
- The server runs as a subprocess of the AI client
- Stop/restart the AI client to stop the server
- Or kill the process manually:

```bash
# Find the process
ps aux | grep server.py

# Kill by PID
kill <PID>

# Or kill all Python processes running the server
pkill -f "server.py"
```

### Testing a Tool

```bash
cd /home/slave/Desktop/tuiTest/mcp-server-demo
source venv/bin/activate

# Test initialize
echo '{"jsonrpc":"2.0","method":"initialize","params":{"capabilities":{},"clientInfo":{"name":"test","version":"1.0.0"},"protocolVersion":"2024-11-05"},"id":1}' | python src/server.py

# Test git_list_repos tool (from correct directory)
echo -e '{"jsonrpc":"2.0","method":"initialize","params":{"capabilities":{},"clientInfo":{"name":"test","version":"1.0.0"},"protocolVersion":"2024-11-05"},"id":0}\n{"jsonrpc":"2.0","method":"tools/call","params":{"name":"git_list_repos","arguments":{}},"id":1}' | python src/server.py
```

**Important:** Always run the server from `/home/slave/Desktop/tuiTest/mcp-server-demo/` directory. The server resolves relative paths based on the current working directory.

### Configuration Files Location

| Client | Config File | Location |
|--------|-------------|----------|
| Claude Desktop | `claude_desktop_config.json` | `~/Library/Application Support/Claude/` |
| Claude Code | `.mcp.json` | `~/.claude/` |
| Cursor | Settings UI | Features → MCP Servers |
| Windsurf | Settings UI | Advanced → MCP Servers |

---

## Conclusion

This MCP server provides a comprehensive foundation for connecting AI assistants to:

- GitHub repositories
- MySQL, PostgreSQL, and MongoDB databases
- Filesystem operations
- Any REST API

Remember these key principles:

1. **Design for AI, not humans** - tools should be high-level and outcome-focused
2. **Security first** - validate inputs, protect secrets, limit permissions
3. **Curate experience** - fewer, better tools beat many confusing ones
4. **Handle errors gracefully** - clear error messages help the AI recover

For more information:
- [MCP Specification](https://spec.modelcontextprotocol.io)
- [FastMCP Documentation](https://fastmcp.io)
- [MCP Community](https://discord.gg/modelcontextprotocol)
