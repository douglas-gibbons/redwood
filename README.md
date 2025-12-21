# Redwood

Redwood is a Python project that implements a Model Context Protocol and a CLI client for Gemini. 

## Motivation

As AI tools get more advanced, they tend to hide away more of the configuration.  Great for end users, but a little annoying if you
want more control.

This tool is pretty raw. It gives full control of the prompt in the one configuration file and makes no assumptions about what
tools to offer the model; leaving it entirely up to the user.

if that's not enough, it's written in Python, and is super simple to modify.

<p align="center">
  <img src="screenshot.png" alt="Redwood Screenshot" width="60%">
</p>


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

Copy the [example configuration file](redwood.example.yaml) into your $HOME/.config directory:

```
cp redwood.example.yaml $HOME/.config/redwood.yaml
```

Then edit the configuration to match your requirements:

* Change the Gemini API key
* Note down where the logs are written (see the logging section)
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

### Running the MCP server

Run `make server` to start the CLI MCP server.


### Testing with inspector

Run

```
npx @modelcontextprotocol/inspector make server
```

# Contributing

Contributions are welcome!

## Reporting Issues

If you find a bug or have a feature request, please open an issue in the repository. Provide as much detail as possible to help us understand and resolve the issue.

## Pull Requests

Please follow these steps to contribute code:

1.  Fork the repository
2.  Create a feature branch (`git checkout -b feature/amazing-feature`)
3.  Commit your changes (`git commit -m 'Add some amazing feature'`)
4.  Run the tests to ensure everything is working:

    ```bash
    make test
    ```

5.  Push to the branch (`git push origin feature/amazing-feature`)
6.  Open a Pull Request

