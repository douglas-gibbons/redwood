import asyncio
from rich.console import Console
from rich.markdown import Markdown
from chat_engine.chat_engine import ChatEngine
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

async def main():
    display = Display()
    engine = ChatEngine(display)
    await engine.register_tools()
    
    while True:
        user_input = display.input()
        await engine.answer_call(user_input)
    
def run():
    asyncio.run(main())
