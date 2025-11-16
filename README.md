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

This is _not_ feature rich, and only works with Gemini. Configuration can be changed from the config.yaml file.

To use, first export an API key:

```
GOOGLE_API_KEY=YOUR_KEY_HERE
```

then run with: 

```
./cli.sh
```

...and `^C` to exit


