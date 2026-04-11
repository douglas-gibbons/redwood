import asyncio
import threading
import logging
import flet as ft
from chat_engine.chat_engine import ChatEngine
from chat_engine.display_interface import DisplayInterface

logger = logging.getLogger(__name__)

class GUI:

    def __init__(self, page: ft.Page):
        self.page = page
        self.page.title = "Redwood"
        self.message_field = None
        self.chat = None
        self.send_button = None
        self.engine = None
        self.display = None

    def initialize(self, display: "Display", engine: ChatEngine):
        self.engine = engine
        self.display = display
        self.message_field = ft.TextField(expand=True, on_submit=self.send_button_click)
        # Use ListView for better scrolling behavior
        self.chat = ft.ListView(expand=True, spacing=10, auto_scroll=False)
        self.send_button = ft.ElevatedButton(
            "Send",
            on_click=self.send_button_click,
        )
        self.page.add(
            self.chat,
            ft.Row([self.message_field, self.send_button]),
        )

    async def send_button_click(self, event=None):
        """Handle user message submission."""
        text = self.message_field.value.strip()
        if not text:
            return
        
        self.message_field.value = ""
        await self.message_field.focus()
        await self.append_to_chat("You", text)
        
        if self.engine:
            await self.engine.answer_call(text)

    async def append_to_chat(self, sender, message, is_markdown=False):
        """Update the UI with new messages."""
        is_user = (sender == "You")
        
        # Select adaptive material colors based on role
        if is_user:
            bgcolor = ft.Colors.PRIMARY_CONTAINER
            padding = ft.padding.only(left=80, top=5, bottom=5)
            text_color = ft.Colors.ON_PRIMARY_CONTAINER
        elif sender == "Redwood":
            bgcolor = ft.Colors.SECONDARY_CONTAINER
            padding = ft.padding.only(right=80, top=5, bottom=5)
            text_color = ft.Colors.ON_SECONDARY_CONTAINER
        elif sender == "System":
            bgcolor = ft.Colors.TERTIARY_CONTAINER
            padding = ft.padding.only(right=80, top=5, bottom=5)
            text_color = ft.Colors.ON_TERTIARY_CONTAINER
        elif sender in ["Warning", "Error"]:
            bgcolor = ft.Colors.ERROR_CONTAINER
            padding = ft.padding.only(right=80, top=5, bottom=5)
            text_color = ft.Colors.ON_ERROR_CONTAINER
        else:
            bgcolor = ft.Colors.SURFACE_VARIANT
            padding = ft.padding.only(right=80, top=5, bottom=5)
            text_color = ft.Colors.ON_SURFACE_VARIANT

        # Render message content
        if is_markdown:
            # Markdown inherits default theme text colors, which generally adapt well.
            content = ft.Markdown(
                message, 
                selectable=True, 
                extension_set=ft.MarkdownExtensionSet.GITHUB_WEB
            )
        else:
            content = ft.Text(f"{message}", color=text_color)

        # Build chat bubble
        bubble = ft.Container(
            content=ft.Column([
                ft.Text(f"{sender}", weight=ft.FontWeight.BOLD, size=12, color=text_color),
                content
            ], spacing=4),
            bgcolor=bgcolor,
            border_radius=ft.border_radius.all(12),
            padding=15,
        )

        # Wrap in a directional container
        wrapper = ft.Container(
            content=bubble,
            padding=padding,
            alignment=ft.Alignment.CENTER_RIGHT if is_user else ft.Alignment.CENTER_LEFT
        )
        
        self.chat.controls.append(wrapper)
        await self.chat.scroll_to(offset=-1, duration=300)
        self.page.update()


class Display(DisplayInterface):

    def __init__(self, gui: GUI):
        self.gui = gui
        
    async def initialize(self, engine: ChatEngine):
        await engine.register_tools()

    async def info(self, message):
        await self.gui.append_to_chat("System", message)

    async def warn(self, message):
        await self.gui.append_to_chat("Warning", message)

    async def error(self, message):
        await self.gui.append_to_chat("Error", message)

    async def markdown(self, prompt):
        await self.gui.append_to_chat("Redwood", prompt, is_markdown=True)
        return prompt

async def main(page: ft.Page):

    gui = GUI(page)
    display = Display(gui)
    engine = ChatEngine(display)

    gui.initialize(display, engine)

    async with asyncio.TaskGroup() as tg:
        tg.create_task(display.initialize(engine))
        tg.create_task(engine.initialize())
    
    page.update()

def run():
    ft.app(target=main)
