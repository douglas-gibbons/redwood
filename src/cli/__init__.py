import asyncio
import os
from google import genai
from rich.console import Console
from rich.markdown import Markdown
from chat_engine.chat_engine import ChatEngine
import mcp_client
import pprint
import logging
from config import Config
import sys
import readline # needed for input() to write to stdout instead of stderr
from chat_engine.display_interface import DisplayInterface

class Display(DisplayInterface):

    def __init__(self):
        self.console = Console()

    def info(self, message):
        self.console.print(message)

    def markdown(self, message):
        self.console.print(Markdown(message))

    def warn(self, message):
        self.console.print(f"[bold red]{message}[/bold red]")

    def error(self, message):
        self.console.print(f"[bold red]{message}[/bold red]")

    def input(self):
        return input(">> ")

def run():
    display = Display()
    engine = ChatEngine(display)
    asyncio.run(engine.engine())

if __name__ == "__main__":
    run()
