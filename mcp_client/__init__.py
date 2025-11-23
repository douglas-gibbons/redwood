import re
from fastmcp import Client
from fastmcp.client.transports import StdioTransport, StreamableHttpTransport

class Server:
    def __init__(self, name, command, args, env, url, headers):
        self.name = name

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

        # Set up the clients
        self.clients = {}
        for server in self.servers:
            
            if server.command is not None:
                transport = StdioTransport(
                    command = server.command,
                    args = server.args,
                    env = server.env if "env" in server else {}
                )
            else:
                transport = StreamableHttpTransport(
                    url = server.url,
                    headers = server.headers
                )

            clean_name = self.sanitize_name(server.name)
            self.clients[clean_name] = Client(transport)
        
    # Returns tuple of server, tool 
    def get_tool_name(self,full_tool_name):
        n = full_tool_name.split("_", 1)
        return n[0], n[1]

    async def list_tools(self):
        all_tools = []
        for server in self.servers:
            clean_name = self.sanitize_name(server.name)
            client = self.clients[clean_name]
            async with client:
                tools = await client.list_tools()
                for tool in tools:
                    tool.name = clean_name + "_" + tool.name

            all_tools += tools

        return all_tools

    async def execute_tool(self, full_tool_name, args):
        server_name, tool_name = self.get_tool_name(full_tool_name)
 
        client = self.clients[server_name]
        async with client:
            response = await client.call_tool(tool_name, args)
        return response
    
    def sanitize_name(self, name):
        return re.sub(r"[^a-zA-Z0-9]", "", name)
