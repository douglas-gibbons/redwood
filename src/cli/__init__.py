import asyncio
from rich.console import Console
from rich.markdown import Markdown
from chat_engine.chat_engine import ChatEngine
import readline # needed for input() to write to stdout instead of stderr
from chat_engine.display_interface import DisplayInterface

class Display(DisplayInterface):

    def __init__(self):
        self.console = Console()

    async def info(self, message):
        self.console.print(message)

    async def markdown(self, message):
        self.console.print(Markdown(message))

    async def warn(self, message):
        self.console.print(f"[bold red]{message}[/bold red]")

    async def error(self, message):
        self.console.print(f"[bold red]{message}[/bold red]")

    def input(self):
        return input(">> ")

async def main():
    display = Display()
    engine = ChatEngine(display)
    await engine.initialize()
    
    while True:
        try:
            await engine.answer_call(display.input())
        except (KeyboardInterrupt, EOFError):
            engine.exit()
    
def run():
    asyncio.run(main())
