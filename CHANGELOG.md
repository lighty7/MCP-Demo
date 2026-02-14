# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added
- Initial MCP server implementation

### Features

#### GitHub Integration
- List issues (`github_list_issues`)
- Get issue details (`github_get_issue`)
- Create issues (`github_create_issue`)
- List pull requests (`github_list_pulls`)
- Get file content (`github_get_file_content`)

#### Local Git Operations
- List repositories (`git_list_repos`)
- List branches (`git_list_branches`)
- Get status (`git_get_status`)
- Get commit log (`git_get_log`)
- Show commit details (`git_show_commit`)
- List tags (`git_list_tags`)
- Get file diff (`git_get_file_diff`)
- Get current branch (`git_get_current_branch`)
- Checkout branch (`git_checkout_branch`)
- Stage files (`git_stage_file`)
- Commit changes (`git_commit`)
- Pull from remote (`git_pull`)
- Push to remote (`git_push`)
- Get remote info (`git_get_remote`)
- Clone repository (`git_clone`)

#### Database Support
- MySQL: Execute queries, list tables, describe tables
- PostgreSQL: Execute queries, list tables, describe tables
- MongoDB: Find, aggregate, count, list collections

#### Filesystem Operations
- Read file (`filesystem_read_file`)
- Write file (`filesystem_write_file`)
- List directory (`filesystem_list_directory`)
- Create directory (`filesystem_create_directory`)
- Delete file (`filesystem_delete_file`)
- Search files (`filesystem_search`)

#### Custom API
- GET request (`custom_api_get`)
- POST request (`custom_api_post`)
- PUT request (`custom_api_put`)
- DELETE request (`custom_api_delete`)

### Resources
- Database status (`config://database-status`)
- GitHub status (`config://github-status`)
- Custom API status (`config://custom-api-status`)
- Local Git status (`config://local-git-status`)

### Prompts
- Database query helper
- File system helper
- GitHub helper
- Local Git helper

---

## [1.0.0] - 2026-02-14

### Added
- Initial release
- Universal MCP server with GitHub, Local Git, MySQL, PostgreSQL, MongoDB, Filesystem, and Custom API support
- Configuration files for Claude Desktop, Claude Code, and Cursor
- Comprehensive documentation

---

## Template

```markdown
## [Version] - YYYY-MM-DD

### Added
- New feature

### Changed
- Updated existing feature

### Deprecated
- Feature that will be removed

### Removed
- Removed feature

### Fixed
- Bug fix

### Security
- Security update
```

---

## Upgrade Guide

### From 0.x to 1.0.0
This is the initial release. Follow the installation instructions in README.md.
```
