from fastmcp import Client
from fastmcp.client.auth import OAuth
from fastmcp.client.transports import StdioTransport, StreamableHttpTransport, SSETransport
from fastmcp.client.logging import LogMessage
from pathlib import Path
import logging
import re


logging.getLogger().handlers.clear()
logger = logging.getLogger(__name__)

# Returns tuple of server, tool 
def get_tool_name(full_tool_name):
    logger.debug("Getting tool name for " + full_tool_name)
    n = full_tool_name.split("_", 1)
    if len(n) != 2:
        logger.error("Invalid tool name: " + full_tool_name)
        return None, None
    return n[0], n[1]

def toolResponse(message_type, message):
        return {
            "message_type": message_type,
            "message": message
        }

def dict_to_server(d):
    return Server(
            name=d.get("name"),
            ask=d.get("ask", False),
            command=d.get("command", None),
            args=d.get("args", []),
            env=d.get("env", {}),
            url=d.get("url", None),
            headers=d.get("headers", {}),
            protocol=d.get("protocol", None)
    )

# Handles logging for servers and forwards to standard logging
LOGGING_LEVEL_MAP = logging.getLevelNamesMapping()
async def log_handler(message: LogMessage):
    msg = message.data.get('msg')
    extra = message.data.get('extra')
    # Convert the MCP log level to a Python log level
    level = LOGGING_LEVEL_MAP.get(message.level.upper(), logging.INFO)
    # Log the message using the standard logging library
    logger.log(level, msg, extra=extra)

class Server:
    def __init__(self, name, ask, command, args, env, url, headers, protocol):
        self.name = name
        self.ask = ask

        # STDIO transport parameters
        self.command = command
        self.args = args
        self.env = env

        # HTTP transport parameters
        self.url = url
        self.headers = headers
        self.protocol = protocol

class MCPClient:
    
    def __init__(self, servers: list[Server], log_file: str | Path | None = None):

        self.servers = servers
        self.log_file = Path(log_file) if log_file else None
        self.clients = {}
        
        
        # Set up other servers
        for server in self.servers:
            
            clean_name = self.sanitize_name(server.name)
            
            # STDIO Transport
            if server.command is not None:
                transport = StdioTransport(
                    command = server.command,
                    args = server.args,
                    env = server.env,
                    log_file = self.log_file
                )
                self.clients[clean_name] = Client(transport, log_handler=log_handler)
            
            # HTTP or SSE Transport
            elif server.url is not None:
                if server.protocol == "sse":
                    transport = SSETransport(
                        url = server.url,
                        headers = server.headers,
                        auth = OAuth(mcp_url = server.url)
                    )
                else:
                    transport = StreamableHttpTransport(
                        url = server.url,
                        headers = server.headers,
                        auth = OAuth(mcp_url = server.url)
                    )
                self.clients[clean_name] = Client(transport)
                
            
    async def list_tools(self):

        all_tools = []

        for name, client in self.clients.items():
            logger.debug("Listing tools for client " + name)
            async with client:
                tools = await client.list_tools()
                for tool in tools:
                    tool.name = name + "_" + tool.name
            all_tools += tools

        return all_tools

    async def execute_tool(self, full_tool_name, args):
        server_name, tool_name = get_tool_name(full_tool_name)
        if server_name is None or tool_name is None:
            logger.error("Invalid tool name: " + full_tool_name)
            return toolResponse("error", "Invalid tool name: " + full_tool_name)


        if self.can_execute_tool(server_name, tool_name, args):
            client = self.clients[server_name]
            async with client:
                logger.debug("Executing tool " + full_tool_name + " with args " + str(args))
                try:
                    response = await client.call_tool(tool_name, args)
                except Exception as e:
                    logger.error("Error calling tool " + full_tool_name + ": " + str(e))
                    return toolResponse("error", "Error calling tool " + full_tool_name + ": " + str(e))
                logger.debug("Received response from tool " + full_tool_name + ": " + str(response))
                
                if response.content is not None and len(response.content) > 0 and response.content[0].text is not None:
                    return {"result": response.content[0].text}
                else:
                    logger.debug("Tool " + full_tool_name + " returned no content")
                    return toolResponse("error", "tool returned no content")
            
        else:
            logger.debug("User denied execution of tool " + full_tool_name)
            return toolResponse("error", "User denied execution of tool " + full_tool_name)

    def sanitize_name(self, name):
        return re.sub(r"[^a-zA-Z0-9]", "", name)

    def can_execute_tool(self, server_name, tool_name, args):
        
        for server in self.servers:
            if self.sanitize_name(server.name) == server_name:
                if server.ask is None or server.ask == True:
                    print("\033[92mExecute tool", server_name, tool_name, "with args", args, "?\033[91m (Y/n)\033[0m")
                    user_input = input(">> ")
                    if user_input.lower() == "y" or user_input.lower() == "yes" or user_input == "":
                        return True
                    else:
                        return False
                else:
                    return True
        return False
