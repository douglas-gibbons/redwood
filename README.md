# Redwood

Redwood is a Python project that implements a CLI client for Gemini.

There's also an MCP server with basic tools to help with tasks such as telling the time, running local commands and storing data.

## Motivation

As AI tools get more advanced, they tend to hide away more of the configuration.  Great for end users, but a little annoying if you
want more control.

This tool is pretty raw. It gives full control of the prompt in the one configuration file and makes no assumptions about what
tools to offer the model; leaving it entirely up to the user.

If that's not enough, it's written in Python, and is super simple to modify, should you want to.

<p align="center">
  <img src="screenshot.png" alt="Redwood Screenshot" width="60%">
</p>


## Quick Start for the CLI app

1. Install uv (`brew install uv`)

2. Download the example configuration file and copy it to your $HOME/.config directory:
   
   ```bash
   curl -o ~/.config/redwood.yaml https://raw.githubusercontent.com/douglas-gibbons/redwood/main/redwood.example.yaml
   ```

3. Edit `~/.config/redwood.yaml` to add your [Gemini API key](https://ai.google.dev/gemini-api/docs/api-key), configure MCP servers, and maybe tweak the prompt.

4. Run the CLI:

   ```bash
   uvx --from git+https://github.com/douglas-gibbons/redwood cli
   ```

## Development

### Requirements

This python app requires:

- uv (`brew install uv`)
- make (`brew install make`)

Check out the code somewhere with:

`git clone https://github.com/douglas-gibbons/redwood.git`

or

`git clone git@github.com:douglas-gibbons/redwood.git`


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

```bash
make cli
```

Special commands:

* Type `tools` to list available tools.
* Type `exit` to exit.


### Running the MCP server

Run `make server` to start the MCP server.


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

