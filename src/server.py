import os
import json
from pathlib import Path
from typing import Any
from datetime import datetime

from fastmcp import FastMCP
from pydantic import BaseModel
import pymysql
import pymongo
import psycopg2
import psycopg2.extras
import requests
from github import Github
from sqlalchemy import create_engine, text
import aiofiles
import git
from git import Repo

mcp = FastMCP("Universal MCP Server")

DATABASE_CONFIG = {
    "mysql": {
        "host": os.getenv("MYSQL_HOST", "localhost"),
        "port": int(os.getenv("MYSQL_PORT", "3306")),
        "user": os.getenv("MYSQL_USER", "root"),
        "password": os.getenv("MYSQL_PASSWORD", ""),
        "database": os.getenv("MYSQL_DATABASE", "test"),
    },
    "postgresql": {
        "host": os.getenv("POSTGRES_HOST", "localhost"),
        "port": int(os.getenv("POSTGRES_PORT", "5432")),
        "user": os.getenv("POSTGRES_USER", "postgres"),
        "password": os.getenv("POSTGRES_PASSWORD", ""),
        "database": os.getenv("POSTGRES_DATABASE", "test"),
    },
    "mongodb": {
        "host": os.getenv("MONGO_HOST", "localhost"),
        "port": int(os.getenv("MONGO_PORT", "27017")),
        "database": os.getenv("MONGO_DATABASE", "test"),
    },
}

GITHUB_CONFIG = {
    "token": os.getenv("GITHUB_TOKEN", ""),
    "owner": os.getenv("GITHUB_OWNER", ""),
    "repo": os.getenv("GITHUB_REPO", ""),
}

CUSTOM_API_CONFIG = {
    "base_url": os.getenv("CUSTOM_API_URL", ""),
    "api_key": os.getenv("CUSTOM_API_KEY", ""),
    "headers": json.loads(os.getenv("CUSTOM_API_HEADERS", "{}")),
}

LOCAL_GIT_CONFIG = {
    "base_path": os.getenv("LOCAL_GIT_BASE_PATH", "/home/slave/Desktop/tuiTest"),
    "default_branch": os.getenv("LOCAL_GIT_DEFAULT_BRANCH", "main"),
}


class MySQLConnection:
    def __init__(self):
        self.config = DATABASE_CONFIG["mysql"]

    def get_connection(self):
        return pymysql.connect(
            host=self.config["host"],
            port=self.config["port"],
            user=self.config["user"],
            password=self.config["password"],
            database=self.config["database"],
            cursorclass=pymysql.cursors.DictCursor,
        )


class PostgreSQLConnection:
    def __init__(self):
        self.config = DATABASE_CONFIG["postgresql"]

    def get_connection(self):
        return psycopg2.connect(
            host=self.config["host"],
            port=self.config["port"],
            user=self.config["user"],
            password=self.config["password"],
            database=self.config["database"],
        )


class MongoDBConnection:
    def __init__(self):
        self.config = DATABASE_CONFIG["mongodb"]

    def get_client(self):
        return pymongo.MongoClient(
            host=self.config["host"],
            port=self.config["port"],
        )


mysql_conn = MySQLConnection()
postgresql_conn = PostgreSQLConnection()
mongodb_conn = MongoDBConnection()


# =============================================================================
# GITHub TOOLS
# =============================================================================


@mcp.tool()
async def github_list_issues(
    state: str = "open",
    limit: int = 10,
) -> str:
    """List issues from a GitHub repository.
    
    Args:
        state: Issue state filter - 'open', 'closed', or 'all'
        limit: Maximum number of issues to return (default 10)
    
    Returns:
        JSON string containing list of issues with title, number, state, and body
    """
    if not GITHUB_CONFIG["token"]:
        return json.dumps({"error": "GITHUB_TOKEN not configured"})
    
    try:
        g = Github(GITHUB_CONFIG["token"])
        repo = g.get_repo(f"{GITHUB_CONFIG['owner']}/{GITHUB_CONFIG['repo']}")
        issues = repo.get_issues(state=state)
        
        result = []
        for issue in issues[:limit]:
            result.append({
                "number": issue.number,
                "title": issue.title,
                "state": issue.state,
                "body": issue.body,
                "labels": [label.name for label in issue.labels],
                "created_at": issue.created_at.isoformat() if issue.created_at else None,
            })
        
        return json.dumps(result, indent=2)
    except Exception as e:
        return json.dumps({"error": str(e)})


@mcp.tool()
async def github_get_issue(issue_number: int) -> str:
    """Get a specific GitHub issue by number.
    
    Args:
        issue_number: The issue number to retrieve
    
    Returns:
        JSON string containing issue details
    """
    if not GITHUB_CONFIG["token"]:
        return json.dumps({"error": "GITHUB_TOKEN not configured"})
    
    try:
        g = Github(GITHUB_CONFIG["token"])
        repo = g.get_repo(f"{GITHUB_CONFIG['owner']}/{GITHUB_CONFIG['repo']}")
        issue = repo.get_issue(issue_number)
        
        result = {
            "number": issue.number,
            "title": issue.title,
            "state": issue.state,
            "body": issue.body,
            "labels": [label.name for label in issue.labels],
            "comments": issue.comments,
            "created_at": issue.created_at.isoformat() if issue.created_at else None,
            "updated_at": issue.updated_at.isoformat() if issue.updated_at else None,
        }
        
        return json.dumps(result, indent=2)
    except Exception as e:
        return json.dumps({"error": str(e)})


@mcp.tool()
async def github_create_issue(
    title: str,
    body: str = "",
    labels: list[str] | None = None,
) -> str:
    """Create a new GitHub issue.
    
    Args:
        title: Issue title (required)
        body: Issue description body
        labels: List of label names to add
    
    Returns:
        JSON string containing created issue details
    """
    if not GITHUB_CONFIG["token"]:
        return json.dumps({"error": "GITHUB_TOKEN not configured"})
    
    try:
        g = Github(GITHUB_CONFIG["token"])
        repo = g.get_repo(f"{GITHUB_CONFIG['owner']}/{GITHUB_CONFIG['repo']}")
        issue = repo.create_issue(title=title, body=body, labels=labels or [])
        
        result = {
            "number": issue.number,
            "title": issue.title,
            "state": issue.state,
            "url": issue.html_url,
        }
        
        return json.dumps(result, indent=2)
    except Exception as e:
        return json.dumps({"error": str(e)})


@mcp.tool()
async def github_list_pulls(state: str = "open") -> str:
    """List pull requests from a GitHub repository.
    
    Args:
        state: PR state filter - 'open', 'closed', or 'all'
    
    Returns:
        JSON string containing list of pull requests
    """
    if not GITHUB_CONFIG["token"]:
        return json.dumps({"error": "GITHUB_TOKEN not configured"})
    
    try:
        g = Github(GITHUB_CONFIG["token"])
        repo = g.get_repo(f"{GITHUB_CONFIG['owner']}/{GITHUB_CONFIG['repo']}")
        pulls = repo.get_pulls(state=state)
        
        result = []
        for pr in pulls[:20]:
            result.append({
                "number": pr.number,
                "title": pr.title,
                "state": pr.state,
                "body": pr.body,
                "head_branch": pr.head.ref,
                "base_branch": pr.base.ref,
                "created_at": pr.created_at.isoformat() if pr.created_at else None,
            })
        
        return json.dumps(result, indent=2)
    except Exception as e:
        return json.dumps({"error": str(e)})


@mcp.tool()
async def github_get_file_content(path: str, ref: str = "main") -> str:
    """Get file content from a GitHub repository.
    
    Args:
        path: File path in the repository (e.g., 'src/main.py')
        ref: Branch or commit SHA
    
    Returns:
        JSON string containing file content (base64 encoded)
    """
    if not GITHUB_CONFIG["token"]:
        return json.dumps({"error": "GITHUB_TOKEN not configured"})
    
    try:
        g = Github(GITHUB_CONFIG["token"])
        repo = g.get_repo(f"{GITHUB_CONFIG['owner']}/{GITHUB_CONFIG['repo']}")
        file_content = repo.get_contents(path, ref=ref)
        
        result = {
            "name": file_content.name,
            "path": file_content.path,
            "content": file_content.content,
            "encoding": file_content.encoding,
            "size": file_content.size,
            "sha": file_content.sha,
        }
        
        return json.dumps(result, indent=2)
    except Exception as e:
        return json.dumps({"error": str(e)})


# =============================================================================
# MySQL TOOLS
# =============================================================================


@mcp.tool()
async def mysql_execute_query(query: str, params: list | None = None) -> str:
    """Execute a read-only SQL query on MySQL database.
    
    Args:
        query: SQL SELECT query to execute (read-only for safety)
        params: Optional list of query parameters
    
    Returns:
        JSON string containing query results
    """
    if not DATABASE_CONFIG["mysql"]["database"]:
        return json.dumps({"error": "MySQL not configured"})
    
    try:
        conn = mysql_conn.get_connection()
        try:
            with conn.cursor() as cursor:
                cursor.execute(query, params or ())
                results = cursor.fetchall()
                
                if not results:
                    return json.dumps({"message": "No results found", "rows": []})
                
                return json.dumps({
                    "rows": results,
                    "count": len(results),
                }, indent=2, default=str)
        finally:
            conn.close()
    except Exception as e:
        return json.dumps({"error": str(e)})


@mcp.tool()
async def mysql_list_tables() -> str:
    """List all tables in the MySQL database.
    
    Returns:
        JSON string containing list of table names
    """
    if not DATABASE_CONFIG["mysql"]["database"]:
        return json.dumps({"error": "MySQL not configured"})
    
    try:
        conn = mysql_conn.get_connection()
        try:
            with conn.cursor() as cursor:
                cursor.execute("SHOW TABLES")
                tables = cursor.fetchall()
                
                table_names = [list(row.values())[0] for row in tables]
                return json.dumps({"tables": table_names}, indent=2)
        finally:
            conn.close()
    except Exception as e:
        return json.dumps({"error": str(e)})


@mcp.tool()
async def mysql_describe_table(table_name: str) -> str:
    """Get table schema/structure from MySQL.
    
    Args:
        table_name: Name of the table to describe
    
    Returns:
        JSON string containing table schema
    """
    if not DATABASE_CONFIG["mysql"]["database"]:
        return json.dumps({"error": "MySQL not configured"})
    
    try:
        conn = mysql_conn.get_connection()
        try:
            with conn.cursor() as cursor:
                cursor.execute(f"DESCRIBE `{table_name}`")
                columns = cursor.fetchall()
                
                return json.dumps({
                    "table": table_name,
                    "columns": columns,
                }, indent=2, default=str)
        finally:
            conn.close()
    except Exception as e:
        return json.dumps({"error": str(e)})


# =============================================================================
# PostgreSQL TOOLS
# =============================================================================


@mcp.tool()
async def postgresql_execute_query(query: str, params: list | None = None) -> str:
    """Execute a read-only SQL query on PostgreSQL database.
    
    Args:
        query: SQL SELECT query to execute
        params: Optional list of query parameters
    
    Returns:
        JSON string containing query results
    """
    if not DATABASE_CONFIG["postgresql"]["database"]:
        return json.dumps({"error": "PostgreSQL not configured"})
    
    try:
        conn = postgresql_conn.get_connection()
        try:
            with conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor) as cursor:
                cursor.execute(query, params or ())
                results = cursor.fetchall()
                
                if not results:
                    return json.dumps({"message": "No results found", "rows": []})
                
                return json.dumps({
                    "rows": [dict(row) for row in results],
                    "count": len(results),
                }, indent=2, default=str)
        finally:
            conn.close()
    except Exception as e:
        return json.dumps({"error": str(e)})


@mcp.tool()
async def postgresql_list_tables() -> str:
    """List all tables in the PostgreSQL database.
    
    Returns:
        JSON string containing list of table names
    """
    if not DATABASE_CONFIG["postgresql"]["database"]:
        return json.dumps({"error": "PostgreSQL not configured"})
    
    try:
        conn = postgresql_conn.get_connection()
        try:
            with conn.cursor() as cursor:
                cursor.execute("""
                    SELECT table_name 
                    FROM information_schema.tables 
                    WHERE table_schema = 'public'
                """)
                tables = cursor.fetchall()
                
                table_names = [row[0] for row in tables]
                return json.dumps({"tables": table_names}, indent=2)
        finally:
            conn.close()
    except Exception as e:
        return json.dumps({"error": str(e)})


@mcp.tool()
async def postgresql_describe_table(table_name: str) -> str:
    """Get table schema/structure from PostgreSQL.
    
    Args:
        table_name: Name of the table to describe
    
    Returns:
        JSON string containing table schema
    """
    if not DATABASE_CONFIG["postgresql"]["database"]:
        return json.dumps({"error": "PostgreSQL not configured"})
    
    try:
        conn = postgresql_conn.get_connection()
        try:
            with conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor) as cursor:
                cursor.execute(f"""
                    SELECT column_name, data_type, is_nullable, column_default
                    FROM information_schema.columns
                    WHERE table_name = %s
                    ORDER BY ordinal_position
                """, (table_name,))
                columns = cursor.fetchall()
                
                return json.dumps({
                    "table": table_name,
                    "columns": [dict(col) for col in columns],
                }, indent=2, default=str)
        finally:
            conn.close()
    except Exception as e:
        return json.dumps({"error": str(e)})


# =============================================================================
# MongoDB TOOLS
# =============================================================================


@mcp.tool()
async def mongodb_list_collections() -> str:
    """List all collections in the MongoDB database.
    
    Returns:
        JSON string containing list of collection names
    """
    if not DATABASE_CONFIG["mongodb"]["database"]:
        return json.dumps({"error": "MongoDB not configured"})
    
    try:
        client = mongodb_conn.get_client()
        db = client[DATABASE_CONFIG["mongodb"]["database"]]
        collections = db.list_collection_names()
        
        return json.dumps({"collections": collections}, indent=2)
    except Exception as e:
        return json.dumps({"error": str(e)})


@mcp.tool()
async def mongodb_find(
    collection: str,
    filter: str = "{}",
    limit: int = 10,
    sort_field: str | None = None,
    sort_order: int = -1,
) -> str:
    """Find documents in a MongoDB collection.
    
    Args:
        collection: Name of the collection
        filter: JSON filter query (default: empty = all documents)
        limit: Maximum number of documents to return (default 10)
        sort_field: Field to sort by (optional)
        sort_order: Sort order: 1 for ascending, -1 for descending
    
    Returns:
        JSON string containing matching documents
    """
    if not DATABASE_CONFIG["mongodb"]["database"]:
        return json.dumps({"error": "MongoDB not configured"})
    
    try:
        client = mongodb_conn.get_client()
        db = client[DATABASE_CONFIG["mongodb"]["database"]]
        coll = db[collection]
        
        query_filter = json.loads(filter)
        
        cursor = coll.find(query_filter).limit(limit)
        
        if sort_field:
            cursor = cursor.sort(sort_field, sort_order)
        
        results = list(cursor)
        
        for doc in results:
            doc["_id"] = str(doc["_id"])
        
        return json.dumps({
            "count": len(results),
            "documents": results,
        }, indent=2, default=str)
    except Exception as e:
        return json.dumps({"error": str(e)})


@mcp.tool()
async def mongodb_aggregate(collection: str, pipeline: str) -> str:
    """Run an aggregation pipeline on a MongoDB collection.
    
    Args:
        collection: Name of the collection
        pipeline: JSON array of aggregation stages
    
    Returns:
        JSON string containing aggregated results
    """
    if not DATABASE_CONFIG["mongodb"]["database"]:
        return json.dumps({"error": "MongoDB not configured"})
    
    try:
        client = mongodb_conn.get_client()
        db = client[DATABASE_CONFIG["mongodb"]["database"]]
        coll = db[collection]
        
        pipeline_stages = json.loads(pipeline)
        
        results = list(coll.aggregate(pipeline_stages))
        
        for doc in results:
            if "_id" in doc:
                doc["_id"] = str(doc["_id"])
        
        return json.dumps({
            "count": len(results),
            "results": results,
        }, indent=2, default=str)
    except Exception as e:
        return json.dumps({"error": str(e)})


@mcp.tool()
async def mongodb_count(collection: str, filter: str = "{}") -> str:
    """Count documents in a MongoDB collection.
    
    Args:
        collection: Name of the collection
        filter: JSON filter query
    
    Returns:
        JSON string containing count
    """
    if not DATABASE_CONFIG["mongodb"]["database"]:
        return json.dumps({"error": "MongoDB not configured"})
    
    try:
        client = mongodb_conn.get_client()
        db = client[DATABASE_CONFIG["mongodb"]["database"]]
        coll = db[collection]
        
        query_filter = json.loads(filter)
        count = coll.count_documents(query_filter)
        
        return json.dumps({"collection": collection, "count": count}, indent=2)
    except Exception as e:
        return json.dumps({"error": str(e)})


# =============================================================================
# FILESYSTEM TOOLS
# =============================================================================


@mcp.tool()
async def filesystem_read_file(path: str) -> str:
    """Read contents of a file.
    
    Args:
        path: Absolute path to the file
    
    Returns:
        JSON string containing file content and metadata
    """
    try:
        file_path = Path(path).resolve()
        
        if not file_path.exists():
            return json.dumps({"error": f"File not found: {path}"})
        
        if not file_path.is_file():
            return json.dumps({"error": f"Not a file: {path}"})
        
        async with aiofiles.open(file_path, "r", encoding="utf-8") as f:
            content = await f.read()
        
        stat = file_path.stat()
        
        return json.dumps({
            "path": str(file_path),
            "content": content,
            "size": stat.st_size,
            "modified": datetime.fromtimestamp(stat.st_mtime).isoformat(),
            "created": datetime.fromtimestamp(stat.st_ctime).isoformat(),
        }, indent=2)
    except Exception as e:
        return json.dumps({"error": str(e)})


@mcp.tool()
async def filesystem_write_file(path: str, content: str) -> str:
    """Write content to a file (creates or overwrites).
    
    Args:
        path: Absolute path to the file
        content: Content to write
    
    Returns:
        JSON string confirming the write operation
    """
    try:
        file_path = Path(path).resolve()
        
        file_path.parent.mkdir(parents=True, exist_ok=True)
        
        async with aiofiles.open(file_path, "w", encoding="utf-8") as f:
            await f.write(content)
        
        return json.dumps({
            "success": True,
            "path": str(file_path),
            "bytes_written": len(content.encode("utf-8")),
        }, indent=2)
    except Exception as e:
        return json.dumps({"error": str(e)})


@mcp.tool()
async def filesystem_list_directory(path: str, pattern: str = "*") -> str:
    """List files and directories in a folder.
    
    Args:
        path: Absolute path to the directory
        pattern: Glob pattern for filtering (default: all files)
    
    Returns:
        JSON string containing directory listing
    """
    try:
        dir_path = Path(path).resolve()
        
        if not dir_path.exists():
            return json.dumps({"error": f"Directory not found: {path}"})
        
        if not dir_path.is_dir():
            return json.dumps({"error": f"Not a directory: {path}"})
        
        items = []
        for item in dir_path.glob(pattern):
            stat = item.stat()
            items.append({
                "name": item.name,
                "path": str(item),
                "type": "directory" if item.is_dir() else "file",
                "size": stat.st_size,
                "modified": datetime.fromtimestamp(stat.st_mtime).isoformat(),
            })
        
        return json.dumps({
            "path": str(dir_path),
            "items": items,
            "count": len(items),
        }, indent=2)
    except Exception as e:
        return json.dumps({"error": str(e)})


@mcp.tool()
async def filesystem_create_directory(path: str) -> str:
    """Create a new directory.
    
    Args:
        path: Absolute path for the new directory
    
    Returns:
        JSON string confirming the operation
    """
    try:
        dir_path = Path(path).resolve()
        dir_path.mkdir(parents=True, exist_ok=True)
        
        return json.dumps({
            "success": True,
            "path": str(dir_path),
        }, indent=2)
    except Exception as e:
        return json.dumps({"error": str(e)})


@mcp.tool()
async def filesystem_delete_file(path: str) -> str:
    """Delete a file.
    
    Args:
        path: Absolute path to the file to delete
    
    Returns:
        JSON string confirming the operation
    """
    try:
        file_path = Path(path).resolve()
        
        if not file_path.exists():
            return json.dumps({"error": f"File not found: {path}"})
        
        file_path.unlink()
        
        return json.dumps({
            "success": True,
            "path": str(file_path),
        }, indent=2)
    except Exception as e:
        return json.dumps({"error": str(e)})


@mcp.tool()
async def filesystem_search(
    directory: str,
    pattern: str,
    max_results: int = 20,
) -> str:
    """Search for files matching a pattern.
    
    Args:
        directory: Root directory to search
        pattern: Glob pattern (e.g., '*.py', '**/*.js')
        max_results: Maximum number of results (default 20)
    
    Returns:
        JSON string containing matching file paths
    """
    try:
        dir_path = Path(directory).resolve()
        
        if not dir_path.exists():
            return json.dumps({"error": f"Directory not found: {directory}"})
        
        matches = list(dir_path.glob(pattern))[:max_results]
        
        results = []
        for match in matches:
            results.append({
                "name": match.name,
                "path": str(match),
                "type": "directory" if match.is_dir() else "file",
            })
        
        return json.dumps({
            "directory": str(dir_path),
            "pattern": pattern,
            "matches": results,
            "count": len(results),
        }, indent=2)
    except Exception as e:
        return json.dumps({"error": str(e)})


# =============================================================================
# CUSTOM API TOOLS
# =============================================================================


@mcp.tool()
async def custom_api_get(endpoint: str, params: str = "{}") -> str:
    """Make a GET request to a custom API.
    
    Args:
        endpoint: API endpoint path (e.g., '/users')
        params: JSON string of query parameters
    
    Returns:
        JSON string containing API response
    """
    if not CUSTOM_API_CONFIG["base_url"]:
        return json.dumps({"error": "CUSTOM_API_URL not configured"})
    
    try:
        headers = {
            "Content-Type": "application/json",
            **CUSTOM_API_CONFIG["headers"],
        }
        
        if CUSTOM_API_CONFIG["api_key"]:
            headers["Authorization"] = f"Bearer {CUSTOM_API_CONFIG['api_key']}"
        
        url = f"{CUSTOM_API_CONFIG['base_url'].rstrip('/')}/{endpoint.lstrip('/')}"
        query_params = json.loads(params)
        
        response = requests.get(url, headers=headers, params=query_params, timeout=30)
        response.raise_for_status()
        
        return json.dumps({
            "status_code": response.status_code,
            "data": response.json() if response.content else None,
        }, indent=2)
    except Exception as e:
        return json.dumps({"error": str(e)})


@mcp.tool()
async def custom_api_post(endpoint: str, body: str = "{}") -> str:
    """Make a POST request to a custom API.
    
    Args:
        endpoint: API endpoint path (e.g., '/users')
        body: JSON string of request body
    
    Returns:
        JSON string containing API response
    """
    if not CUSTOM_API_CONFIG["base_url"]:
        return json.dumps({"error": "CUSTOM_API_URL not configured"})
    
    try:
        headers = {
            "Content-Type": "application/json",
            **CUSTOM_API_CONFIG["headers"],
        }
        
        if CUSTOM_API_CONFIG["api_key"]:
            headers["Authorization"] = f"Bearer {CUSTOM_API_CONFIG['api_key']}"
        
        url = f"{CUSTOM_API_CONFIG['base_url'].rstrip('/')}/{endpoint.lstrip('/')}"
        request_body = json.loads(body)
        
        response = requests.post(url, headers=headers, json=request_body, timeout=30)
        response.raise_for_status()
        
        return json.dumps({
            "status_code": response.status_code,
            "data": response.json() if response.content else None,
        }, indent=2)
    except Exception as e:
        return json.dumps({"error": str(e)})


@mcp.tool()
async def custom_api_put(endpoint: str, body: str = "{}") -> str:
    """Make a PUT request to a custom API.
    
    Args:
        endpoint: API endpoint path (e.g., '/users/1')
        body: JSON string of request body
    
    Returns:
        JSON string containing API response
    """
    if not CUSTOM_API_CONFIG["base_url"]:
        return json.dumps({"error": "CUSTOM_API_URL not configured"})
    
    try:
        headers = {
            "Content-Type": "application/json",
            **CUSTOM_API_CONFIG["headers"],
        }
        
        if CUSTOM_API_CONFIG["api_key"]:
            headers["Authorization"] = f"Bearer {CUSTOM_API_CONFIG['api_key']}"
        
        url = f"{CUSTOM_API_CONFIG['base_url'].rstrip('/')}/{endpoint.lstrip('/')}"
        request_body = json.loads(body)
        
        response = requests.put(url, headers=headers, json=request_body, timeout=30)
        response.raise_for_status()
        
        return json.dumps({
            "status_code": response.status_code,
            "data": response.json() if response.content else None,
        }, indent=2)
    except Exception as e:
        return json.dumps({"error": str(e)})


@mcp.tool()
async def custom_api_delete(endpoint: str) -> str:
    """Make a DELETE request to a custom API.
    
    Args:
        endpoint: API endpoint path (e.g., '/users/1')
    
    Returns:
        JSON string containing API response
    """
    if not CUSTOM_API_CONFIG["base_url"]:
        return json.dumps({"error": "CUSTOM_API_URL not configured"})
    
    try:
        headers = {
            "Content-Type": "application/json",
            **CUSTOM_API_CONFIG["headers"],
        }
        
        if CUSTOM_API_CONFIG["api_key"]:
            headers["Authorization"] = f"Bearer {CUSTOM_API_CONFIG['api_key']}"
        
        url = f"{CUSTOM_API_CONFIG['base_url'].rstrip('/')}/{endpoint.lstrip('/')}"
        
        response = requests.delete(url, headers=headers, timeout=30)
        response.raise_for_status()
        
        return json.dumps({
            "status_code": response.status_code,
            "message": "Resource deleted successfully",
        }, indent=2)
    except Exception as e:
        return json.dumps({"error": str(e)})


# =============================================================================
# LOCAL GIT TOOLS
# =============================================================================


def _get_git_repo(repo_path: str) -> Repo:
    base_path = Path(LOCAL_GIT_CONFIG["base_path"])
    full_path = (base_path / repo_path).resolve()
    
    if not str(full_path).startswith(str(base_path)):
        raise ValueError("Access denied: path outside allowed directory")
    
    if not full_path.exists():
        raise ValueError(f"Repository not found: {repo_path}")
    
    if not (full_path / ".git").exists():
        raise ValueError(f"Not a git repository: {repo_path}")
    
    return Repo(full_path)


@mcp.tool()
async def git_list_repos() -> str:
    """List available local git repositories.
    
    Returns:
        JSON string containing list of available repositories
    """
    try:
        base_path = Path(LOCAL_GIT_CONFIG["base_path"]).resolve()
        
        if not base_path.exists():
            return json.dumps({"error": "Base path not configured or does not exist"})
        
        repos = []
        for item in base_path.iterdir():
            if item.is_dir() and (item / ".git").exists():
                repos.append({
                    "name": item.name,
                    "path": str(item.relative_to(base_path)),
                })
        
        return json.dumps({
            "base_path": str(base_path),
            "repositories": repos,
            "count": len(repos),
        }, indent=2)
    except Exception as e:
        return json.dumps({"error": str(e)})


@mcp.tool()
async def git_list_branches(repo_path: str) -> str:
    """List branches in a local git repository.
    
    Args:
        repo_path: Relative path to the repository from base path
    
    Returns:
        JSON string containing list of branches
    """
    try:
        repo = _get_git_repo(repo_path)
        
        branches = {
            "current": repo.active_branch.name,
            "local": [b.name for b in repo.branches],
            "remote": [r.name for r in repo.remote().refs] if repo.remotes else [],
        }
        
        return json.dumps(branches, indent=2)
    except Exception as e:
        return json.dumps({"error": str(e)})


@mcp.tool()
async def git_get_status(repo_path: str) -> str:
    """Get working tree status of a local git repository.
    
    Args:
        repo_path: Relative path to the repository
    
    Returns:
        JSON string containing modified, staged, and untracked files
    """
    try:
        repo = _get_git_repo(repo_path)
        
        status = repo.git.status("--porcelain")
        
        modified = []
        staged = []
        untracked = []
        
        for line in status.split("\n"):
            if not line:
                continue
            index_status = line[0]
            worktree_status = line[1]
            file_path = line[3:] if len(line) > 3 else line[2:]
            
            if worktree_status == "?":
                untracked.append(file_path)
            elif index_status in ("M", "A", "D"):
                staged.append(file_path)
            elif worktree_status == "M":
                modified.append(file_path)
        
        return json.dumps({
            "repo": repo_path,
            "branch": repo.active_branch.name,
            "is_dirty": repo.is_dirty(),
            "modified": modified,
            "staged": staged,
            "untracked": untracked,
        }, indent=2)
    except Exception as e:
        return json.dumps({"error": str(e)})


@mcp.tool()
async def git_get_log(
    repo_path: str,
    max_count: int = 10,
    branch: str | None = None,
) -> str:
    """Get commit history from a local git repository.
    
    Args:
        repo_path: Relative path to the repository
        max_count: Maximum number of commits to return (default 10)
        branch: Branch name to get log from (optional, defaults to current branch)
    
    Returns:
        JSON string containing commit history
    """
    try:
        repo = _get_git_repo(repo_path)
        
        if branch:
            commit_range = branch
        else:
            commit_range = repo.active_branch.name
        
        commits = list(repo.iter_commits(commit_range, max_count=max_count))
        
        result = []
        for commit in commits:
            result.append({
                "sha": commit.hexsha[:7],
                "full_sha": commit.hexsha,
                "message": commit.message.strip(),
                "author": str(commit.author),
                "author_email": commit.author.email,
                "committed_date": datetime.fromtimestamp(commit.committed_date).isoformat(),
                "parents": [p.hexsha[:7] for p in commit.parents],
            })
        
        return json.dumps({
            "repo": repo_path,
            "branch": branch or repo.active_branch.name,
            "commits": result,
            "count": len(result),
        }, indent=2)
    except Exception as e:
        return json.dumps({"error": str(e)})


@mcp.tool()
async def git_show_commit(repo_path: str, sha: str) -> str:
    """Show details of a specific commit.
    
    Args:
        repo_path: Relative path to the repository
        sha: Commit SHA (full or short)
    
    Returns:
        JSON string containing commit details
    """
    try:
        repo = _get_git_repo(repo_path)
        
        commit = repo.commit(sha)
        
        result = {
            "sha": commit.hexsha[:7],
            "full_sha": commit.hexsha,
            "message": commit.message.strip(),
            "author": str(commit.author),
            "author_email": commit.author.email,
            "committed_date": datetime.fromtimestamp(commit.committed_date).isoformat(),
            "parents": [p.hexsha[:7] for p in commit.parents],
            "diff": commit.diff(commit.parents[0]).__str__() if commit.parents else "Initial commit",
        }
        
        return json.dumps(result, indent=2)
    except Exception as e:
        return json.dumps({"error": str(e)})


@mcp.tool()
async def git_list_tags(repo_path: str) -> str:
    """List tags in a local git repository.
    
    Args:
        repo_path: Relative path to the repository
    
    Returns:
        JSON string containing list of tags
    """
    try:
        repo = _get_git_repo(repo_path)
        
        tags = []
        for tag in repo.tags:
            tags.append({
                "name": tag.name,
                "commit": tag.commit.hexsha[:7] if tag.commit else None,
            })
        
        return json.dumps({
            "repo": repo_path,
            "tags": tags,
            "count": len(tags),
        }, indent=2)
    except Exception as e:
        return json.dumps({"error": str(e)})


@mcp.tool()
async def git_get_file_diff(repo_path: str, file_path: str, branch: str | None = None) -> str:
    """Get diff for a specific file.
    
    Args:
        repo_path: Relative path to the repository
        file_path: Path to the file
        branch: Branch to compare against (optional)
    
    Returns:
        JSON string containing file diff
    """
    try:
        repo = _get_git_repo(repo_path)
        
        if branch:
            diff = repo.git.diff(branch, "--", file_path)
        else:
            diff = repo.git.diff("HEAD", "--", file_path)
        
        return json.dumps({
            "repo": repo_path,
            "file": file_path,
            "branch": branch or repo.active_branch.name,
            "diff": diff or "No changes",
        }, indent=2)
    except Exception as e:
        return json.dumps({"error": str(e)})


@mcp.tool()
async def git_get_current_branch(repo_path: str) -> str:
    """Get current branch of a local git repository.
    
    Args:
        repo_path: Relative path to the repository
    
    Returns:
        JSON string containing current branch name
    """
    try:
        repo = _get_git_repo(repo_path)
        
        return json.dumps({
            "repo": repo_path,
            "branch": repo.active_branch.name,
        }, indent=2)
    except Exception as e:
        return json.dumps({"error": str(e)})


@mcp.tool()
async def git_checkout_branch(repo_path: str, branch: str, create: bool = False) -> str:
    """Checkout a branch in a local git repository.
    
    Args:
        repo_path: Relative path to the repository
        branch: Branch name to checkout
        create: Create new branch if True (default False)
    
    Returns:
        JSON string confirming the operation
    """
    try:
        repo = _get_git_repo(repo_path)
        
        if create and branch not in [b.name for b in repo.branches]:
            new_branch = repo.create_head(branch)
            new_branch.checkout()
            action = "created and checked out"
        else:
            repo.git.checkout(branch)
            action = "checked out"
        
        return json.dumps({
            "success": True,
            "repo": repo_path,
            "branch": branch,
            "action": action,
        }, indent=2)
    except Exception as e:
        return json.dumps({"error": str(e)})


@mcp.tool()
async def git_stage_file(repo_path: str, file_path: str | None = None) -> str:
    """Stage files in a local git repository.
    
    Args:
        repo_path: Relative path to the repository
        file_path: Specific file to stage (optional, stages all if None)
    
    Returns:
        JSON string confirming the operation
    """
    try:
        repo = _get_git_repo(repo_path)
        
        if file_path:
            repo.git.add(file_path)
            staged_files = [file_path]
        else:
            repo.git.add("--all")
            status = repo.git.status("--porcelain")
            staged_files = [line[3:] for line in status.split("\n") if line and line[0] in ("A", "M")]
        
        return json.dumps({
            "success": True,
            "repo": repo_path,
            "staged": staged_files,
        }, indent=2)
    except Exception as e:
        return json.dumps({"error": str(e)})


@mcp.tool()
async def git_commit(repo_path: str, message: str, author_name: str | None = None, author_email: str | None = None) -> str:
    """Commit staged changes in a local git repository.
    
    Args:
        repo_path: Relative path to the repository
        message: Commit message
        author_name: Override author name (optional)
        author_email: Override author email (optional)
    
    Returns:
        JSON string containing commit details
    """
    try:
        repo = _get_git_repo(repo_path)
        
        if not repo.is_dirty():
            return json.dumps({"error": "Nothing to commit - working tree is clean"})
        
        if author_name or author_email:
            env = {}
            if author_name:
                env["GIT_AUTHOR_NAME"] = author_name
            if author_email:
                env["GIT_AUTHOR_EMAIL"] = author_email
            
            with repo.git.EnvironmentOverride(env):
                commit = repo.index.commit(message)
        else:
            commit = repo.index.commit(message)
        
        return json.dumps({
            "success": True,
            "repo": repo_path,
            "sha": commit.hexsha[:7],
            "full_sha": commit.hexsha,
            "message": message,
        }, indent=2)
    except Exception as e:
        return json.dumps({"error": str(e)})


@mcp.tool()
async def git_pull(repo_path: str) -> str:
    """Pull changes from remote in a local git repository.
    
    Args:
        repo_path: Relative path to the repository
    
    Returns:
        JSON string containing pull result
    """
    try:
        repo = _get_git_repo(repo_path)
        
        if not repo.remotes:
            return json.dumps({"error": "No remotes configured"})
        
        origin = repo.remotes.origin
        info = origin.pull()
        
        return json.dumps({
            "success": True,
            "repo": repo_path,
            "remote": "origin",
            "fetched_commits": len(info),
            "branch": repo.active_branch.name,
        }, indent=2)
    except Exception as e:
        return json.dumps({"error": str(e)})


@mcp.tool()
async def git_push(repo_path: str, remote: str = "origin", branch: str | None = None) -> str:
    """Push changes to remote in a local git repository.
    
    Args:
        repo_path: Relative path to the repository
        remote: Remote name (default: origin)
        branch: Branch to push (default: current branch)
    
    Returns:
        JSON string containing push result
    """
    try:
        repo = _get_git_repo(repo_path)
        
        if remote not in [r.name for r in repo.remotes]:
            return json.dumps({"error": f"Remote '{remote}' not found"})
        
        target_branch = branch or repo.active_branch.name
        remote_ref = f"{remote}/{target_branch}"
        
        repo.git.push(remote, target_branch)
        
        return json.dumps({
            "success": True,
            "repo": repo_path,
            "remote": remote,
            "branch": target_branch,
            "message": f"Pushed to {remote_ref}",
        }, indent=2)
    except Exception as e:
        return json.dumps({"error": str(e)})


@mcp.tool()
async def git_get_remote(repo_path: str) -> str:
    """Get remote information for a local git repository.
    
    Args:
        repo_path: Relative path to the repository
    
    Returns:
        JSON string containing remote information
    """
    try:
        repo = _get_git_repo(repo_path)
        
        if not repo.remotes:
            return json.dumps({"remotes": [], "message": "No remotes configured"})
        
        remotes = []
        for remote in repo.remotes:
            remotes.append({
                "name": remote.name,
                "urls": list(remote.urls),
                "push_urls": list(remote.push_urls),
            })
        
        return json.dumps({
            "repo": repo_path,
            "remotes": remotes,
        }, indent=2)
    except Exception as e:
        return json.dumps({"error": str(e)})


@mcp.tool()
async def git_clone(source_url: str, target_path: str) -> str:
    """Clone a git repository to local path.
    
    Args:
        source_url: Source git repository URL
        target_path: Relative path where to clone
    
    Returns:
        JSON string containing clone result
    """
    try:
        base_path = Path(LOCAL_GIT_CONFIG["base_path"]).resolve()
        full_path = (base_path / target_path).resolve()
        
        if not str(full_path).startswith(str(base_path)):
            return json.dumps({"error": "Access denied: target path outside allowed directory"})
        
        if full_path.exists():
            return json.dumps({"error": f"Target path already exists: {target_path}"})
        
        full_path.parent.mkdir(parents=True, exist_ok=True)
        
        Repo.clone_from(source_url, str(full_path))
        
        return json.dumps({
            "success": True,
            "source_url": source_url,
            "target_path": str(full_path.relative_to(base_path)),
            "message": "Repository cloned successfully",
        }, indent=2)
    except Exception as e:
        return json.dumps({"error": str(e)})


# =============================================================================
# RESOURCES
# =============================================================================


@mcp.resource("config://database-status")
async def get_database_status() -> str:
    """Get status of all configured databases."""
    status = {}
    
    for db_type in ["mysql", "postgresql", "mongodb"]:
        configured = bool(DATABASE_CONFIG[db_type].get("database"))
        status[db_type] = "configured" if configured else "not configured"
    
    return json.dumps(status, indent=2)


@mcp.resource("config://github-status")
async def get_github_status() -> str:
    """Get GitHub integration status."""
    status = {
        "configured": bool(GITHUB_CONFIG["token"]),
        "owner": GITHUB_CONFIG["owner"] or "not set",
        "repo": GITHUB_CONFIG["repo"] or "not set",
    }
    return json.dumps(status, indent=2)


@mcp.resource("config://custom-api-status")
async def get_custom_api_status() -> str:
    """Get custom API integration status."""
    status = {
        "configured": bool(CUSTOM_API_CONFIG["base_url"]),
        "base_url": CUSTOM_API_CONFIG["base_url"] or "not set",
    }
    return json.dumps(status, indent=2)


@mcp.resource("config://local-git-status")
async def get_local_git_status() -> str:
    """Get local git configuration status."""
    base_path = Path(LOCAL_GIT_CONFIG["base_path"]).resolve()
    
    repos = []
    if base_path.exists():
        for item in base_path.iterdir():
            if item.is_dir() and (item / ".git").exists():
                repos.append(item.name)
    
    status = {
        "base_path": str(base_path),
        "configured": base_path.exists(),
        "available_repos": repos,
    }
    return json.dumps(status, indent=2)


# =============================================================================
# PROMPTS
# =============================================================================


@mcp.prompt()
def database_query_helper() -> str:
    """Generate a helpful prompt for database queries."""
    return """You are helping the user query databases. Follow these guidelines:

1. For MySQL queries:
   - Always use parameterized queries when possible
   - Be careful with string values - escape properly
   - Use SHOW TABLES to see available tables first

2. For PostgreSQL queries:
   - Use $1, $2, etc. for parameterized queries
   - Check table schemas before running complex queries

3. For MongoDB queries:
   - Use proper JSON filter syntax
   - Remember MongoDB uses different operators than SQL

4. Safety:
   - Never execute DELETE or DROP without confirmation
   - Always explain what the query will do first
   - Limit results to prevent large outputs

When the user asks to query data:
1. Ask which database if not specified
2. Suggest appropriate queries
3. Execute and explain results
"""


@mcp.prompt()
def file_system_helper() -> str:
    """Generate a helpful prompt for file operations."""
    return """You are helping the user with file system operations. Follow these guidelines:

1. Reading files:
   - Check if file exists first
   - Handle encoding issues gracefully
   - Show file size and modification time

2. Writing files:
   - Confirm before overwriting existing files
   - Create parent directories if needed
   - Show what was written

3. Searching:
   - Use appropriate glob patterns
   - Limit results to prevent overwhelming output

4. Safety:
   - Never delete files without confirmation
   - Warn about large files
   - Respect file permissions

When the user asks to work with files:
1. Understand the goal
2. Choose the appropriate operation
3. Execute safely and report results
"""


@mcp.prompt()
def github_helper() -> str:
    """Generate a helpful prompt for GitHub operations."""
    return """You are helping the user with GitHub operations. Follow these guidelines:

1. Listing issues/PRs:
   - Show relevant details (number, title, state, labels)
   - Use appropriate state filters
   - Limit results to prevent overflow

2. Creating issues:
   - Validate title is provided
   - Suggest appropriate labels
   - Show the created issue URL

3. Reading files:
   - Show file path and size
   - Content is base64 encoded - decode if needed
   - Handle binary files appropriately

4. Safety:
   - Never push or commit without explicit permission
   - Warn about rate limits
   - Confirm destructive operations

When the user asks to work with GitHub:
1. Understand the goal
2. Choose the appropriate operation
3. Report results clearly with URLs
"""


@mcp.prompt()
def local_git_helper() -> str:
    """Generate a helpful prompt for local git operations."""
    return """You are helping the user with local git operations. Follow these guidelines:

1. Repository Discovery:
   - Use git_list_repos to see available repositories
   - Check git_get_status before making changes
   - List branches with git_list_branches

2. Viewing History:
   - Use git_get_log to see commit history
   - Show commit details with git_show_commit
   - Display diffs with git_get_file_diff

3. Making Changes:
   - Always check git_get_status first
   - Use git_stage_file to stage specific files
   - Never commit without a clear message
   - Confirm before pushing to remote

4. Branch Operations:
   - List branches before checking out
   - Use git_checkout_branch with create=True for new branches
   - Always specify the repo_path correctly

5. Safety:
   - Never force push without explicit permission
   - Confirm destructive operations
   - Warn about uncommitted changes before checkout
   - Backup important work before reset operations

When the user asks to work with local git:
1. Identify the repository path
2. Check current status first
3. Choose the appropriate operation
4. Report results clearly with commit SHAs
"""


if __name__ == "__main__":
    import sys
    
    transport = "stdio"
    for arg in sys.argv[1:]:
        if arg.startswith("--transport="):
            transport = arg.split("=", 1)[1]
    
    if transport == "sse":
        from fastmcp.transport import SSETransport
        
        mcp.run(transport=SSETransport(host="0.0.0.0", port=8080))
    else:
        mcp.run()
