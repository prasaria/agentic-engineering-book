# Connect Claude Code to tools via MCP

> Learn how to connect Claude Code to your tools with the Model Context Protocol.

Claude Code can connect to hundreds of external tools and data sources through the [Model Context Protocol (MCP)](https://modelcontextprotocol.io/introduction), an open source standard for AI-tool integrations. MCP servers give Claude Code access to your tools, databases, and APIs.

## What you can do with MCP

With MCP servers connected, you can ask Claude Code to:

* **Implement features from issue trackers**: "Add the feature described in JIRA issue ENG-4521 and create a PR on GitHub."
* **Analyze monitoring data**: "Check Sentry and Statsig to check the usage of the feature described in ENG-4521."
* **Query databases**: "Find emails of 10 random users who used feature ENG-4521, based on our PostgreSQL database."
* **Integrate designs**: "Update our standard email template based on the new Figma designs that were posted in Slack"
* **Automate workflows**: "Create Gmail drafts inviting these 10 users to a feedback session about the new feature."

## Installing MCP servers

MCP servers can be configured in three different ways depending on your needs:

### Option 1: Add a remote HTTP server

HTTP servers are the recommended option for connecting to remote MCP servers. This is the most widely supported transport for cloud-based services.

```bash
# Basic syntax
claude mcp add --transport http <name> <url>

# Real example: Connect to Notion
claude mcp add --transport http notion https://mcp.notion.com/mcp

# Example with Bearer token
claude mcp add --transport http secure-api https://api.example.com/mcp \
  --header "Authorization: Bearer your-token"
```

### Option 2: Add a remote SSE server

> **Warning**: The SSE (Server-Sent Events) transport is deprecated. Use HTTP servers instead, where available.

```bash
# Basic syntax
claude mcp add --transport sse <name> <url>

# Real example: Connect to Asana
claude mcp add --transport sse asana https://mcp.asana.com/sse

# Example with authentication header
claude mcp add --transport sse private-api https://api.company.com/sse \
  --header "X-API-Key: your-key-here"
```

### Option 3: Add a local stdio server

Stdio servers run as local processes on your machine. They're ideal for tools that need direct system access or custom scripts.

```bash
# Basic syntax
claude mcp add --transport stdio <name> <command> [args...]

# Real example: Add Airtable server
claude mcp add --transport stdio airtable --env AIRTABLE_API_KEY=YOUR_KEY \
  -- npx -y airtable-mcp-server
```

> **Note**: The `--` (double dash) separates Claude's own CLI flags from the command and arguments that get passed to the MCP server.

### Managing your servers

Once configured, you can manage your MCP servers with these commands:

```bash
# List all configured servers
claude mcp list

# Get details for a specific server
claude mcp get github

# Remove a server
claude mcp remove github

# (within Claude Code) Check server status
/mcp
```

**Tips**:
* Use the `--scope` flag to specify where the configuration is stored:
  * `local` (default): Available only to you in the current project
  * `project`: Shared with everyone in the project via `.mcp.json` file
  * `user`: Available to you across all projects
* Set environment variables with `--env` flags (for example, `--env KEY=value`)
* Configure MCP server startup timeout using the MCP_TIMEOUT environment variable
* Use `/mcp` to authenticate with remote servers that require OAuth 2.0 authentication

## MCP installation scopes

MCP servers can be configured at three different scope levels:

### Local scope

Local-scoped servers are stored in `~/.claude.json` under your project's path. These servers remain private to you and are only accessible when working within the current project directory.

```bash
# Add a local-scoped server (default)
claude mcp add --transport http stripe https://mcp.stripe.com

# Explicitly specify local scope
claude mcp add --transport http stripe --scope local https://mcp.stripe.com
```

### Project scope

Project-scoped servers enable team collaboration by storing configurations in a `.mcp.json` file at your project's root directory.

```bash
# Add a project-scoped server
claude mcp add --transport http paypal --scope project https://mcp.paypal.com/mcp
```

The resulting `.mcp.json` file follows this format:

```json
{
  "mcpServers": {
    "shared-server": {
      "command": "/path/to/server",
      "args": [],
      "env": {}
    }
  }
}
```

### User scope

User-scoped servers are stored in `~/.claude.json` and provide cross-project accessibility.

```bash
# Add a user server
claude mcp add --transport http hubspot --scope user https://mcp.hubspot.com/anthropic
```

### Environment variable expansion in `.mcp.json`

Claude Code supports environment variable expansion in `.mcp.json` files:

* `${VAR}` - Expands to the value of environment variable `VAR`
* `${VAR:-default}` - Expands to `VAR` if set, otherwise uses `default`

Example:

```json
{
  "mcpServers": {
    "api-server": {
      "type": "http",
      "url": "${API_BASE_URL:-https://api.example.com}/mcp",
      "headers": {
        "Authorization": "Bearer ${API_KEY}"
      }
    }
  }
}
```

## Practical examples

### Example: Monitor errors with Sentry

```bash
# 1. Add the Sentry MCP server
claude mcp add --transport http sentry https://mcp.sentry.dev/mcp

# 2. Use /mcp to authenticate with your Sentry account
> /mcp

# 3. Debug production issues
> "What are the most common errors in the last 24 hours?"
> "Show me the stack trace for error ID abc123"
```

### Example: Connect to GitHub for code reviews

```bash
# 1. Add the GitHub MCP server
claude mcp add --transport http github https://api.githubcopilot.com/mcp/

# 2. In Claude Code, authenticate if needed
> /mcp

# 3. Now you can ask Claude to work with GitHub
> "Review PR #456 and suggest improvements"
> "Create a new issue for the bug we just found"
```

### Example: Query your PostgreSQL database

```bash
# 1. Add the database server with your connection string
claude mcp add --transport stdio db -- npx -y @bytebase/dbhub \
  --dsn "postgresql://readonly:pass@prod.db.com:5432/analytics"

# 2. Query your database naturally
> "What's our total revenue this month?"
> "Show me the schema for the orders table"
```

## Authenticate with remote MCP servers

Many cloud-based MCP servers require authentication. Claude Code supports OAuth 2.0 for secure connections.

1. Add the server that requires authentication
2. Use the `/mcp` command within Claude Code
3. Follow the steps in your browser to login

## Add MCP servers from JSON configuration

If you have a JSON configuration for an MCP server, you can add it directly:

```bash
# Basic syntax
claude mcp add-json <name> '<json>'

# Example: Adding an HTTP server with JSON configuration
claude mcp add-json weather-api '{"type":"http","url":"https://api.weather.com/mcp","headers":{"Authorization":"Bearer token"}}'
```

## Import MCP servers from Claude Desktop

If you've already configured MCP servers in Claude Desktop, you can import them:

```bash
# Import servers from Claude Desktop
claude mcp add-from-claude-desktop
```

## Use Claude Code as an MCP server

You can use Claude Code itself as an MCP server that other applications can connect to:

```bash
# Start Claude as a stdio MCP server
claude mcp serve
```

You can use this in Claude Desktop by adding this configuration to claude_desktop_config.json:

```json
{
  "mcpServers": {
    "claude-code": {
      "type": "stdio",
      "command": "claude",
      "args": ["mcp", "serve"],
      "env": {}
    }
  }
}
```

## Use MCP resources

MCP servers can expose resources that you can reference using @ mentions:

1. Type `@` in your prompt to see available resources
2. Reference a specific resource: `@server:protocol://resource/path`
3. Multiple resource references in a single prompt are supported

## Use MCP prompts as slash commands

MCP servers can expose prompts that become available as slash commands:

1. Type `/` to see all available commands, including those from MCP servers
2. MCP prompts appear with the format `/mcp__servername__promptname`
3. Execute prompts with arguments space-separated after the command

## Enterprise MCP configuration

For organizations that need centralized control over MCP servers, Claude Code supports:

1. **Exclusive control with `managed-mcp.json`**: Deploy a fixed set of MCP servers that users cannot modify
2. **Policy-based control with allowlists/denylists**: Allow users to add their own servers, but restrict which ones are permitted

System administrators deploy configuration files to system-wide directories:
* macOS: `/Library/Application Support/ClaudeCode/managed-mcp.json`
* Linux and WSL: `/etc/claude-code/managed-mcp.json`
* Windows: `C:\Program Files\ClaudeCode\managed-mcp.json`

---

> Source: https://code.claude.com/docs/en/mcp
> Updated: 2025-12-25
