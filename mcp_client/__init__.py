import re
from fastmcp import Client
from fastmcp.client.transports import StdioTransport, StreamableHttpTransport

# Import tools to register them with MCP
import tools.mcptime
import tools.storage
import tools.command

# Returns tuple of server, tool 
def get_tool_name(full_tool_name):
    n = full_tool_name.split("_", 1)
    return n[0], n[1]

class ToolResponse:
    def __init__(self, message_type, message):
        self.structured_content = {
            "message_type": message_type,
            "message": message
        }

class Server:
    def __init__(self, name, ask, command, args, env, url, headers):
        self.name = name
        self.ask = ask

        # STDIO transport parameters
        self.command = command
        self.args = args
        self.env = env

        # HTTP transport parameters
        self.url = url
        self.headers = headers

class MCPClient:
    
    def __init__(self, servers: list[Server]):

        self.servers = servers
        self.clients = {}
            
        # Set up other servers
        for server in self.servers:
            
            if server.command is not None:
                transport = StdioTransport(
                    command = server.command,
                    args = server.args if "args" in server else [],
                    env = server.env if "env" in server else {}
                )
            elif server.url is not None:
                transport = StreamableHttpTransport(
                    url = server.url,
                    headers = server.headers
                )

            clean_name = self.sanitize_name(server.name)
            self.clients[clean_name] = Client(transport)
            
    async def list_tools(self):

        all_tools = []

        for name, client in self.clients.items():
            async with client:
                tools = await client.list_tools()
                for tool in tools:
                    tool.name = name + "_" + tool.name
            all_tools += tools

        return all_tools

    async def execute_tool(self, full_tool_name, args):
        server_name, tool_name = get_tool_name(full_tool_name)
        if self.can_execute_tool(full_tool_name, args):
            client = self.clients[server_name]
            async with client:
                response = await client.call_tool(tool_name, args)
            return response
        else:
            return ToolResponse("error", "User denied execution of tool " + full_tool_name)

    def sanitize_name(self, name):
        return re.sub(r"[^a-zA-Z0-9]", "", name)

    def can_execute_tool(self, full_tool_name, args):
        server_name, tool_name = get_tool_name(full_tool_name)
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
