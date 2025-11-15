# Redwood

Helper functions for Agents. The storage mechanism is intentionally vague; use prompts to
direct its use.

## Installing

Requirements:

- uv (`brew install uv`)

The first time you run `run.sh` it will set up the python virtual environment and install the packages it needs.

## Adding to an Agent

Add server.sh as an STDIO MCP server

## Testing with inspector

Run

```
npx @modelcontextprotocol/inspector `pwd`/server.sh
```
