# Redwood

## Requirements

This python app requires:

- uv (`brew install uv`)
- make (`brew install make`)

Check out the code somewhere with:

`git clone https://github.com/douglas-gibbons/redwood.git`

or

`git clone git@github.com:douglas-gibbons/redwood.git`


## CLI chat interface

The CLI application is a simple chat interface for use with Gemini.

### Configuration

Copy the example configuration file into your $HOME/.config directory:

```
cp redwood.example.yaml ~/.config/redwood.yaml
```

Then edit the configuration to match your requirements:

* Change the Gemini API key
* Note down where the logs are written (`logging.file`)
* Add any MCP servers you want to use. There are some examples that you can uncomment

### Running the CLI

Run this command on a terminal from where you have the code checked out:

```
make cli
```

Special commands:

* Type `tools` to list available tools.
* Type `exit` to exit.

## MCP Tools

There are helper functions for Agents in MCP form.

The storage mechanism is intentionally vague; use prompts to direct its use.

### Adding the MCP tools to an Agent

Add server.sh as an STDIO MCP server

### Testing with inspector

Run

```
npx @modelcontextprotocol/inspector `pwd`/server.sh
```

# Contributing

Contributions are welcome! Please follow these steps:

1.  Fork the repository
2.  Create a feature branch (`git checkout -b feature/amazing-feature`)
3.  Commit your changes (`git commit -m 'Add some amazing feature'`)
4.  Run the tests to ensure everything is working:

    ```bash
    make test
    ```

5.  Push to the branch (`git push origin feature/amazing-feature`)
6.  Open a Pull Request

