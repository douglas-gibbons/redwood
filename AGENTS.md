# Redwood: Agent Instructions

Welcome to the Redwood codebase! This document is designed to help AI agents understand the structure, architecture, and common commands used in this project.

## Overview
Redwood is a CLI and UI client for Gemini, which includes an MCP (Model Context Protocol) server. It allows interaction with large language models and provides them with tools to execute tasks locally on the user's system, such as scraping web pages, taking notes in a database, generating images, and executing local terminal commands.

## Getting Started

The project uses `uv` for dependency management and `make` for common commands. 

There is no need to manually activate a virtual environment. Use `uv run` or the `make` targets provided.

### Common Commands
- `make test` : Runs the test suite using `pytest`. Always run this after making changes to verify you haven't broken anything.
- `make cli` : Runs the terminal-based CLI application.
- `make ui` : Runs the Tkinter/Flet-based graphical user interface application.
- `make server` : Runs the main MCP server (which includes various tools like database, time, web search).

### Configuration
On first run, Redwood generates a configuration file at `~/.config/redwood.yaml` where the user defines their Gemini API key, configures MCP servers, and modifies prompts.

## Project Structure

The source code is located in the `src/` directory.

- `src/cli/` - The entry point for the terminal-based CLI application.
- `src/ui/` - The entry point for the graphical user interface application.
- `src/server/` - The main MCP server that exposes tools (database, scraping, time, cmd line, etc.) to the language model.
- `src/chat_engine/` - Contains the core chat loop and logic used to communicate with the Gemini API. 
- `src/config/` - Manages parsing and loading the `~/.config/redwood.yaml` settings.
- `src/database/` - Manages the SQLite database used by the MCP tools.
- `src/mcp_client/` - Logic for the CLI/UI to connect to and communicate with MCP servers.
- `src/image_generator/` - A separate MCP server dedicated to generating images.
- `src/agent/` - Contains an LLM agent tool / MCP agent logic.
- `test/` - The `pytest` test suite.

## Development Patterns

- **Dependencies**: Dependencies are defined in `pyproject.toml`. Notable ones include `mcp`, `fastmcp`, `google-genai`, `flet`, and `beautifulsoup4`.
- **MCP Servers**: The project heavily utilizes MCP. When adding new tools, they are typically added to an MCP server (e.g., `src/server/` using the `@mcp.tool` decorator from `fastmcp` or `mcp`).
- **Tests**: Write your tests in the `test/` directory. Ensure any modified or new behavior is covered by tests.
- **Client/Server separation**: The actual tools are run out-of-process via the MCP server. The `cli` or `ui` acts as a client that routes the model's requests to these servers. 
