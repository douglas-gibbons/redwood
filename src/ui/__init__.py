import asyncio
import threading
import logging
import flet as ft
from chat_engine.chat_engine import ChatEngine
from chat_engine.display_interface import DisplayInterface

logger = logging.getLogger(__name__)

class Display(DisplayInterface):

    def __init__(self,page: ft.Page):
        
        self.page = page
        self.page.title = "Redwood"
        
        self.message_field = ft.TextField(expand=True, on_submit=self.send_button_click)

        # Use ListView for better scrolling behavior
        self.chat = ft.ListView(expand=True, spacing=10, auto_scroll=True)

        self.send_button = ft.ElevatedButton(
            "Send",
            on_click=self.send_button_click,
        )

        self.page.add(
            self.chat,
            ft.Row([self.message_field, self.send_button]),
        )
        self.engine = None
    
    def info(self, message):
        self.append_to_chat("System", message)

    def warn(self, message):
        self.append_to_chat("Warning", message)

    def error(self, message):
        self.append_to_chat("Error", message)

    def markdown(self, prompt):
        self.append_to_chat("Redwood", prompt, is_markdown=True)
        return prompt


    async def send_button_click(self, event=None):
        """Handle user message submission."""
        text = self.message_field.value.strip()
        if not text:
            return
        
        self.message_field.value = ""
        self.message_field.focus()
        self.append_to_chat("You", text)
        
        if self.engine:
            await self.engine.answer_call(text)

    def append_to_chat(self, sender, message, is_markdown=False):
        """Update the UI with new messages."""
        if is_markdown:
            self.chat.controls.append(ft.Text(f"{sender}:", weight=ft.FontWeight.BOLD))
            content = ft.Markdown(
                message, 
                selectable=True, 
                extension_set=ft.MarkdownExtensionSet.GITHUB_WEB
            )
        else:
            content = ft.Text(f"{sender}: {message}")
            
        self.chat.controls.append(content)
        self.page.update()

async def main(page: ft.Page):
    ui = Display(page)
    engine = ChatEngine(ui)
    ui.engine = engine  # Link the engine to the UI for callbacks
    await engine.register_tools()
    page.update()

def run():
    ft.app(target=main)
