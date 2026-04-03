import asyncio
import os
import threading
import logging
import tkinter as tk
from tkinter import scrolledtext

from google import genai
import mcp_client
from config import Config

DEFAULT_CONFIG_FILE = os.path.expanduser("~/.config/redwood.yaml")

logging.getLogger().handlers.clear()
logger = logging.getLogger(__name__)

class RedwoodUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Redwood AI")
        self.root.geometry("800x600")
        
        # UI Setup
        self.chat_display = scrolledtext.ScrolledText(self.root, wrap=tk.WORD, state='disabled')
        self.chat_display.pack(padx=10, pady=10, fill=tk.BOTH, expand=True)
        
        input_frame = tk.Frame(self.root)
        input_frame.pack(padx=10, pady=(0, 10), fill=tk.X)
        
        self.user_input = tk.Entry(input_frame)
        self.user_input.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 10))
        self.user_input.bind("<Return>", lambda e: self.send_message())
        
        self.send_button = tk.Button(input_frame, text="Send", command=self.send_message)
        self.send_button.pack(side=tk.RIGHT)
        
        # Menu
        menubar = tk.Menu(self.root)
        self.root.config(menu=menubar)
        
        command_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Commands", menu=command_menu)
        command_menu.add_command(label="List Tools", command=self.cmd_tools)
        command_menu.add_command(label="Set Location", command=self.cmd_locate)
        command_menu.add_command(label="Reset Conversation", command=self.cmd_reset)
        command_menu.add_separator()
        command_menu.add_command(label="Exit", command=self.root.quit)
        
        # Background thread and event loop for asyncio tasks
        self.loop = asyncio.new_event_loop()
        self.thread = threading.Thread(target=self.start_loop, args=(self.loop,), daemon=True)
        self.thread.start()
        
        # State
        self.config = None
        self.client = None
        self.mcpc = None
        self.tools = []
        self.contents = []
        self.model_name = ""
        self.gemini_config = None
        self.is_processing = False
        
        self.append_to_chat("System", "Starting Redwood UI...")
        self.user_input.config(state='disabled')
        self.send_button.config(state='disabled')
        
        # Initialize async components
        asyncio.run_coroutine_threadsafe(self.initialize_async(), self.loop)

    def start_loop(self, loop):
        asyncio.set_event_loop(loop)
        loop.run_forever()

    def append_to_chat(self, sender, message):
        self.chat_display.config(state='normal')
        self.chat_display.insert(tk.END, f"{sender}:\n{message}\n\n")
        self.chat_display.see(tk.END)
        self.chat_display.config(state='disabled')

    async def initialize_async(self):
        try:
            self.config = Config(DEFAULT_CONFIG_FILE)
            if not self.config.exists("model.api_key"):
                raise ValueError("API Key missing from configuration file")

            logging.basicConfig(
                format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                level=self.config.logging.level,
                filemode='a',
                filename=self.config.logging.file
            )

            self.client = genai.Client(api_key=self.config.model.api_key)

            mcp_servers = []
            for server_config in self.config.mcp:
                server = mcp_client.dict_to_server(server_config)
                mcp_servers.append(server)
            
            token_storage_config = None
            if self.config.exists("token_storage.enabled") and self.config.token_storage.enabled:
                token_storage_config = mcp_client.TokenStorageConfig(
                    enabled=self.config.token_storage.enabled,
                    location=os.path.expanduser(self.config.token_storage.location),
                    encryption_key=self.config.token_storage.encryption_key
                )
            self.mcpc = mcp_client.MCPClient(servers=mcp_servers, log_file=self.config.logging.file, token_storage_config=token_storage_config)
            
            self.model_name = self.config.model.name
            self.tools = await self.mcpc.list_tools()

            self.gemini_config = genai.types.GenerateContentConfig(
                tools=self.tools,
                automatic_function_calling=genai.types.AutomaticFunctionCallingConfig(
                    disable=True
                ),
            )
            
            self.set_initial_prompt()
            
            self.root.after(0, self.on_initialized)
        except Exception as e:
            logger.error(f"Initialization error: {e}", exc_info=True)
            self.root.after(0, lambda: self.append_to_chat("Error", f"Failed to initialize: {e}"))

    def on_initialized(self):
        self.append_to_chat("System", f"Ready. Using model: {self.model_name}\nType /help for commands.")
        self.user_input.config(state='normal')
        self.send_button.config(state='normal')
        self.user_input.focus()

    def set_initial_prompt(self):
        if self.config.exists("prompt"):
            self.contents.append(genai.types.Content(role="user", parts=[genai.types.Part(text=self.config.prompt)]))
            self.contents.append(genai.types.Content(role="model", parts=[genai.types.Part(text="Understood")]))

    def send_message(self):
        if self.is_processing:
            return
            
        text = self.user_input.get().strip()
        if not text:
            return
            
        self.user_input.delete(0, tk.END)
        
        if text.startswith("/"):
            self.handle_command(text)
            return

        self.append_to_chat("You", text)
        self.contents.append(genai.types.Content(role="user", parts=[genai.types.Part(text=text)]))
        
        self.set_processing_state(True)
        asyncio.run_coroutine_threadsafe(self.process_chat(), self.loop)

    def set_processing_state(self, is_processing):
        self.is_processing = is_processing
        if is_processing:
            self.user_input.config(state='disabled')
            self.send_button.config(state='disabled')
        else:
            self.user_input.config(state='normal')
            self.send_button.config(state='normal')
            self.user_input.focus()

    def handle_command(self, cmd):
        if cmd in ["/exit", "/x"]:
            self.root.quit()
        elif cmd in ["/tools", "/t"]:
            self.cmd_tools()
        elif cmd in ["/conversation", "/c"]:
            self.append_to_chat("System", str(self.contents))
        elif cmd in ["/locate", "/l"]:
            self.cmd_locate()
        elif cmd in ["/help", "/?"]:
            help_text = (
                "Tools:        '/tools', or '/t' to list available tools\n"
                "Reset:        '/reset', or '/r' to reset the conversation\n"
                "Conversation: '/conversation' or '/c' to show conversation history\n"
                "Locate:       '/locate' or '/l' to tell the model to work in the current directory\n"
                "Help:         '/help' or '/?' to show this help message\n"
                "Exit:         '/exit' or '/x' to quit"
            )
            self.append_to_chat("Help", help_text)
        elif cmd in ["/reset", "/r"]:
            self.cmd_reset()
        else:
            self.append_to_chat("System", f"Unknown command: {cmd}")

    def cmd_tools(self):
        tools_by_server = {}
        for tool in self.tools:
            server_name, tool_name = mcp_client.get_tool_name(tool.name)
            if server_name not in tools_by_server:
                tools_by_server[server_name] = []
            tools_by_server[server_name].append((tool_name, tool))
        
        out = []
        for server_name, server_tools in tools_by_server.items():
            out.append(f"Server: {server_name}")
            for tool_name, tool in server_tools:
                out.append(f"  {tool_name}")
                if tool.description:
                    out.append(f"    {tool.description}")
        self.append_to_chat("Tools", "\n".join(out))

    def cmd_locate(self):
        location = os.getcwd()
        self.contents.append(genai.types.Content(role="user", parts=[genai.types.Part(text=f"Use \"{location}\" as the working directory. File operations should be relative to this directory.")]))
        self.contents.append(genai.types.Content(role="model", parts=[genai.types.Part(text="Understood")]))
        self.append_to_chat("System", f"Location set to {location}")

    def cmd_reset(self):
        self.contents.clear()
        self.set_initial_prompt()
        self.append_to_chat("System", "Conversation history reset.")

    async def process_chat(self):
        try:
            max_model_calls = int(self.config.max_model_calls)
            model_calls = 0
            
            while True:
                if model_calls >= max_model_calls:
                    self.root.after(0, lambda: self.append_to_chat("System", "Max model calls reached. Stopping to prevent costly looping."))
                    break
                    
                model_calls += 1
                
                response = self.client.models.generate_content(
                    model=self.model_name,
                    contents=self.contents,
                    config=self.gemini_config
                )
                
                self.contents.append(response.candidates[0].content)

                if not response.candidates or not response.candidates[0].content or not response.candidates[0].content.parts:
                    self.root.after(0, lambda: self.append_to_chat("Error", "No content returned from model."))
                    logger.warning(f"No content returned from model. Full response: {response}")
                    break

                ask_user = True
                
                for part in response.candidates[0].content.parts:
                    if part.function_call:
                        tool_name = part.function_call.name
                        self.root.after(0, lambda tn=tool_name: self.append_to_chat("System", f"Running tool: {tn}"))
                        
                        tool_response = await self.mcpc.execute_tool(tool_name, part.function_call.args)
                        function_response_part = genai.types.Part.from_function_response(
                            name=tool_name,
                            response=tool_response
                        )
                        resp = genai.types.Content(role="function", parts=[function_response_part])
                        self.contents.append(resp)
                        ask_user = False

                    elif part.text:
                        self.root.after(0, lambda t=part.text: self.append_to_chat("Redwood", t))
                        ask_user = True
                        
                if ask_user:
                    break
                    
        except Exception as e:
            logger.error(f"Error processing chat: {e}", exc_info=True)
            self.root.after(0, lambda e=e: self.append_to_chat("Error", str(e)))
        finally:
            self.root.after(0, lambda: self.set_processing_state(False))

def run():
    root = tk.Tk()
    app = RedwoodUI(root)
    root.mainloop()

if __name__ == "__main__":
    run()
