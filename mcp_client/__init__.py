import pprint
# from fastmcp import Client
from fastmcp import Client, FastMCP
from fastmcp.client.transports import StdioTransport
import yaml

class MCPClient:



    def __init__(self, config_file: str):
        # Load config file
        with open(config_file, "r") as f:
            self.config = yaml.safe_load(f)

        # Set up the clients
        clients = {}
        for mcp_server in self.config["mcp"]:
            
            transport = StdioTransport(
                command = mcp_server["command"],
                args = mcp_server["args"]
            )

            clients[mcp_server["name"]] = Client(transport)
        self.clients = clients
   
    # Returns tuple of server, tool 
    def get_tool_name(self,full_tool_name):
        n = full_tool_name.split("_", 1)
        return n[0], n[1]

    async def list_tools(self):
        all_tools = []
        for mcp_server in self.config["mcp"]:
            client = self.clients[mcp_server["name"]]
            async with client:
                tools = await client.list_tools()
                for tool in tools:
                    tool.name = mcp_server["name"] + "_" + tool.name

            all_tools += tools

        return all_tools

    
    async def execute_tool(self, full_tool_name, args):
        server_name, tool_name = self.get_tool_name(full_tool_name)
 
        client = self.clients[server_name]
        async with client:
            response = await client.call_tool(tool_name, args)
        return response
    