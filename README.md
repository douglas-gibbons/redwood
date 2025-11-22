# Redwood

Helper functions for Agents. The storage mechanism is intentionally vague; use prompts to
direct its use.

There's also a minimalist chat interface.

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

# Running the CLI chat interface

The CPI application is a simple chat interface for use with Gemini.

First create a configuration file in `~/.config/redwood.yaml`:

```
cp redwood.example.yaml ~/.config/redwood.yaml
```

Then edit the configuration to match your requirements. Don't forget to change the Gemini API key.


To run:

```
make cli
```

Type "exit" to exit.
