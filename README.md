# Universal MCP Server

Connect Claude Desktop, Claude Code, Cursor, and other AI assistants to GitHub, local git repositories, databases, filesystems, and custom APIs.

## What is This?

The **Universal MCP Server** is a Model Context Protocol (MCP) server that provides AI assistants with access to:

- **GitHub** - Issues, pull requests, repository files
- **Local Git** - Repository status, commits, branches, staging, commits, push/pull
- **MySQL** - Query databases, list tables, describe schemas
- **PostgreSQL** - Query databases, list tables, describe schemas
- **MongoDB** - Find documents, run aggregations, count
- **Filesystem** - Read/write files, list directories, search
- **Custom APIs** - GET, POST, PUT, DELETE requests to any REST API

## Features

| Category | Capabilities |
|----------|-------------|
| **GitHub** | List issues, get issue details, create issues, list PRs, read files |
| **Local Git** | List repos, branches, status, log, commit, stage, push, pull, clone |
| **MySQL** | Execute queries, list tables, describe table schema |
| **PostgreSQL** | Execute queries, list tables, describe table schema |
| **MongoDB** | Find documents, aggregate, count, list collections |
| **Filesystem** | Read, write, list, create directory, delete, search |
| **Custom API** | GET, POST, PUT, DELETE with custom headers & auth |

## Requirements

- Python 3.10+
- [FastMCP](https://fastmcp.io) (included)
- GitPython (for local git operations)

## Installation

```bash
# Clone or download this repository
cd mcp-server-demo

# Create virtual environment
python -m venv venv

# Activate (Linux/macOS)
source venv/bin/activate

# Activate (Windows)
venv\Scripts\activate

# Install dependencies
pip install -e .
```

Or install dependencies directly:

```bash
pip install fastmcp gitpython pymysql pymongo psycopg2-binary pygithub aiofiles pydantic requests python-dotenv sqlalchemy
```

## Quick Start

### 1. Configure Environment

```bash
# Copy the example environment file
cp config/.env.example config/.env

# Edit with your settings
nano config/.env
```

#### Minimal Config (Local Git Only)

For local git operations, you only need:

```bash
LOCAL_GIT_BASE_PATH=/home/slave/Desktop/tuiTest
LOCAL_GIT_DEFAULT_BRANCH=main
```

#### Full Config (All Features)

```bash
# GitHub
GITHUB_TOKEN=ghp_xxxxxxxxxxxx
GITHUB_OWNER=your-username
GITHUB_REPO=your-repo

# MySQL
MYSQL_HOST=localhost
MYSQL_PORT=3306
MYSQL_USER=root
MYSQL_PASSWORD=your-password
MYSQL_DATABASE=your-db

# PostgreSQL
POSTGRES_HOST=localhost
POSTGRES_PORT=5432
POSTGRES_USER=postgres
POSTGRES_PASSWORD=your-password
POSTGRES_DATABASE=your-db

# MongoDB
MONGO_HOST=localhost
MONGO_PORT=27017
MONGO_DATABASE=your-db

# Custom API
CUSTOM_API_URL=https://api.example.com
CUSTOM_API_KEY=your-api-key

# Local Git
LOCAL_GIT_BASE_PATH=/path/to/your/repos
LOCAL_GIT_DEFAULT_BRANCH=main
```

### 2. Start the Server

```bash
# Standard mode (for AI clients)
python src/server.py

# Or with HTTP/SSE transport
python src/server.py --transport=sse
```

### 3. Connect to AI Client

#### Claude Desktop

1. Open `~/Library/Application Support/Claude/claude_desktop_config.json`
2. Add:

```json
{
  "mcpServers": {
    "universal-mcp": {
      "command": "bash",
      "args": ["-c", "cd /path/to/mcp-server-demo && /path/to/mcp-server-demo/venv/bin/python src/server.py"],
      "env": {
        "LOCAL_GIT_BASE_PATH": "/path/to/your/repos"
      }
    }
  }
}
```

#### Claude Code

1. Open `~/.claude/.mcp.json`
2. Add the same configuration

#### Cursor/Windsurf

1. Open Settings → Features → MCP Servers
2. Add a new server with:
   - Name: `universal-mcp`
   - Command: `bash -c "cd /path/to/mcp-server-demo && /path/to/mcp-server-demo/venv/bin/python src/server.py"`

### 4. Restart Your AI Client

The MCP server tools will be available automatically.

---

## Usage Examples

### GitHub Examples

Here are examples of how to use the GitHub integration with your AI assistant:

#### List Open Issues

> **You:** "Show me the open issues in my GitHub repository"

The AI will call `github_list_issues` with `state: "open"` and return a list of issues with titles, numbers, and labels.

#### List All Issues

> **You:** "List all issues (both open and closed)"

The AI will call `github_list_issues` with `state: "all"`.

#### Get Specific Issue

> **You:** "Show me issue #42"

The AI will call `github_get_issue` with `issue_number: 42`.

#### Create a New Issue

> **You:** "Create a new issue titled 'Fix login bug' with the body 'Users cannot login with special characters in password' and label it as 'bug'"

The AI will call `github_create_issue` with:
- `title`: "Fix login bug"
- `body`: "Users cannot login with special characters in password"
- `labels`: ["bug"]

#### List Pull Requests

> **You:** "Show me the open pull requests"

The AI will call `github_list_pulls` with `state: "open"`.

#### Read a File from Repository

> **You:** "Show me the contents of src/main.py"

The AI will call `github_get_file_content` with `path: "src/main.py"`.

---

### Local Git Examples

Your AI assistant can work with local git repositories. The server automatically discovers repositories in the `LOCAL_GIT_BASE_PATH` directory.

#### List Available Repositories

> **You:** "What git repositories do I have?"

The AI will call `git_list_repos` and return repositories found in your base path.

#### Check Repository Status

> **You:** "What's the status of my tui2026 project?"

The AI will call `git_get_status` with `repo_path: "tui2026"`.

Returns: current branch, modified files, staged files, untracked files.

#### View Commit History

> **You:** "Show me the last 5 commits in redis2026"

The AI will call `git_get_log` with `repo_path: "redis2026", max_count: 5`.

#### View Specific Commit

> **You:** "Show me details about commit abc1234"

The AI will call `git_show_commit` with `repo_path: "your-repo", sha: "abc1234"`.

#### List Branches

> **You:** "What branches are in tui2026?"

The AI will call `git_list_branches` with `repo_path: "tui2026"`.

#### Create a New Branch

> **You:** "Create a new branch called 'feature-auth' in tui2026"

The AI will call `git_checkout_branch` with `repo_path: "tui2026", branch: "feature-auth", create: true`.

#### Switch Branches

> **You:** "Switch to the main branch in redis2026"

The AI will call `git_checkout_branch` with `repo_path: "redis2026", branch: "main"`.

#### Stage Files

> **You:** "Stage all changes in tui2026"

The AI will call `git_stage_file` with `repo_path: "tui2026"`.

#### Commit Changes

> **You:** "Commit my changes in tui2026 with message 'Add new feature'"

The AI will call `git_commit` with `repo_path: "tui2026", message: "Add new feature"`.

#### Pull from Remote

> **You:** "Pull the latest changes in tui2026"

The AI will call `git_pull` with `repo_path: "tui2026"`.

#### Push to Remote

> **You:** "Push my changes to origin call `git_push"

The AI will` with `repo_path: "your-repo"`.

#### Get File Diff

> **You:** "Show me the diff for src/app.py in tui2026"

The AI will call `git_get_file_diff` with `repo_path: "tui2026", file_path: "src/app.py"`.

---

### Database Examples

#### MySQL/PostgreSQL

> **You:** "What tables are in my MySQL database?"

The AI will call `mysql_list_tables` or `postgresql_list_tables`.

> **You:** "Show me the schema for the users table"

The AI will call `mysql_describe_table` or `postgresql_describe_table` with `table_name: "users"`.

> **You:** "Run this query: SELECT * FROM orders WHERE status = 'pending'"

The AI will call `mysql_execute_query` or `postgresql_execute_query` with your query.

#### MongoDB

> **You:** "What collections do I have?"

The AI will call `mongodb_list_collections`.

> **You:** "Find 10 users where age > 21"

The AI will call `mongodb_find` with:
- `collection`: "users"
- `filter`: `{"age": {"$gt": 21}}`
- `limit`: 10

> **You:** "Count how many orders are pending"

The AI will call `mongodb_count` with:
- `collection`: "orders"
- `filter`: `{"status": "pending"}`

---

### Filesystem Examples

#### Read a File

> **You:** "Read the file /path/to/file.txt"

The AI will call `filesystem_read_file` with `path: "/path/to/file.txt"`.

#### Write to a File

> **You:** "Write 'Hello World' to /path/to/newfile.txt"

The AI will call `filesystem_write_file` with:
- `path`: "/path/to/newfile.txt"
- `content`: "Hello World"

#### List Directory

> **You:** "List files in /path/to/directory"

The AI will call `filesystem_list_directory` with `path: "/path/to/directory"`.

#### Search for Files

> **You:** "Find all Python files in my project"

The AI will call `filesystem_search` with:
- `directory`: "/path/to/project"
- `pattern`: "**/*.py"

#### Create Directory

> **You:** "Create a new directory /path/to/newdir"

The AI will call `filesystem_create_directory` with `path: "/path/to/newdir"`.

---

### Custom API Examples

#### GET Request

> **You:** "Fetch the user data from my API"

The AI will call `custom_api_get` with `endpoint: "/users"`.

#### POST Request

> **You:** "Create a new user with name 'John' and email 'john@example.com'"

The AI will call `custom_api_post` with:
- `endpoint`: "/users"
- `body`: `{"name": "John", "email": "john@example.com"}`

#### PUT Request

> **You:** "Update the user with ID 1 to have name 'Jane'"

The AI will call `custom_api_put` with:
- `endpoint`: "/users/1"
- `body`: `{"name": "Jane"}`

#### DELETE Request

> **You:** "Delete the user with ID 1"

The AI will call `custom_api_delete` with `endpoint`: "/users/1".

---

## Configuration Reference

### Environment Variables

| Variable | Description | Required |
|----------|-------------|----------|
| `GITHUB_TOKEN` | GitHub Personal Access Token | For GitHub |
| `GITHUB_OWNER` | GitHub username/org | For GitHub |
| `GITHUB_REPO` | Repository name | For GitHub |
| `MYSQL_*` | MySQL connection settings | For MySQL |
| `POSTGRES_*` | PostgreSQL connection settings | For PostgreSQL |
| `MONGO_*` | MongoDB connection settings | For MongoDB |
| `CUSTOM_API_URL` | Base URL for custom API | For Custom API |
| `CUSTOM_API_KEY` | API key for custom API | For Custom API |
| `LOCAL_GIT_BASE_PATH` | Base directory for local git repos | For Local Git |

### Client Configuration Files

| Client | File | Location |
|--------|------|----------|
| Claude Desktop | `claude_desktop_config.json` | `~/Library/Application Support/Claude/` |
| Claude Code | `.mcp.json` | `~/.claude/` |
| Cursor | Settings UI | Features → MCP Servers |

---

## Project Structure

```
mcp-server-demo/
├── src/
│   └── server.py          # Main MCP server implementation
├── config/
│   ├── .env.example       # Environment variables template
│   ├── claude_desktop_config.json
│   ├── claude_code_config.json
│   └── cursor_config.md
├── docs/
│   └── MCP-SERVER-GUIDE.md  # Full documentation
├── LICENSE                # MIT License
├── README.md              # This file
├── CONTRIBUTING.md        # Contribution guidelines
├── CHANGELOG.md           # Version history
├── pyproject.toml         # Python project config
└── venv/                  # Virtual environment (not tracked)
```

---

## Stopping the Server

### Manual Testing
Press `Ctrl+C` to stop the server.

### Via AI Client
The server runs as a subprocess. Restart the AI client to stop it, or:

```bash
# Find the process
ps aux | grep server.py

# Kill by PID
kill <PID>
```

---

## Troubleshooting

### Server Won't Start

```bash
# Make sure you're in the right directory
cd /path/to/mcp-server-demo

# Activate virtual environment
source venv/bin/activate

# Check Python path
which python  # Should show venv python
```

### Path Errors

The server must run from the project directory. The client configs use a `bash -c` wrapper to ensure this.

### Database Connection Errors

1. Verify database is running
2. Check credentials in `.env`
3. Ensure network connectivity

### GitHub API Errors

1. Verify token is valid
2. Check token has `repo` scope
3. Verify owner/repo are correct

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
    return """You are helping with..."""
```

---

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

---

## Resources

- [MCP Specification](https://spec.modelcontextprotocol.io)
- [FastMCP Documentation](https://fastmcp.io)
- [MCP Community](https://discord.gg/modelcontextprotocol)
- [GitHub API](https://docs.github.com/en/rest)
