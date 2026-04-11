import asyncio
import threading
import logging
import flet as ft
from chat_engine.chat_engine import ChatEngine
from chat_engine.display_interface import DisplayInterface
import os

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
        
        self.page.fonts = {
            "Aleo Bold Italic": "https://raw.githubusercontent.com/google/fonts/master/ofl/aleo/Aleo-BoldItalic.ttf"
        }
        self.page.theme = ft.Theme(font_family="Aleo Bold Italic")
        
        self.message_field = ft.TextField(
            expand=True, 
            on_submit=self.send_button_click,
            multiline=True,
            shift_enter=True,
            autofocus=True
        )
        # Use ListView for better scrolling behavior. 
        # reverse=True anchors the list to the bottom, bypassing the Flet 0.84 scroll defect.
        self.chat = ft.ListView(expand=True, spacing=3, auto_scroll=False, reverse=True)
        self.send_button = ft.ElevatedButton(
            "Send",
            on_click=self.send_button_click,
        )
        self.progress_ring = ft.ProgressRing(width=24, height=24, visible=False)
        self.page.add(
            self.chat,
            ft.Row([self.message_field, self.progress_ring, self.send_button]),
        )

    async def disable_input(self):
        self._processing = True
        self.send_button.disabled = True
        self.progress_ring.visible = True
        self.page.update()

    async def _focus_input(self):
        await asyncio.sleep(0.2)
        try:
            await self.message_field.focus()
        except:
            pass

    async def enable_input(self):
        self._processing = False
        self.send_button.disabled = False
        self.progress_ring.visible = False
        self.page.update()
        self.page.run_task(self._focus_input)

    async def send_button_click(self, event=None):
        """Handle user message submission."""
        if getattr(self, "_processing", False):
            return

        text = self.message_field.value.strip()
        if not text:
            return
        
        self.message_field.value = ""
        await self.append_to_chat("You", text)
        
        if self.engine:
            # Show waiting indicator and disable input
            await self.disable_input()
            
            try:
                await self.engine.answer_call(text)
            finally:
                # Re-enable inputs regardless of errors
                await self.enable_input()

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

        icon_name = None
        if is_user:
            icon_name = ft.Icons.PERSON
        elif sender == "Redwood":
            icon_name = ft.Icons.SMART_TOY
        elif sender == "System":
            icon_name = ft.Icons.SETTINGS
        elif sender in ["Warning", "Error"]:
            icon_name = ft.Icons.WARNING
            
        if icon_name:
            header = ft.Row([
                ft.Icon(icon_name, size=16, color=text_color),
                ft.Text(f"{sender}", size=12, color=text_color)
            ], spacing=5)
        else:
            header = ft.Text(f"{sender}", size=12, color=text_color)

        # Build chat bubble
        bubble = ft.Container(
            content=ft.Column([
                header,
                content
            ], spacing=4),
            bgcolor=bgcolor,
            border_radius=ft.border_radius.all(4),
            padding=8,
        )

        # Wrap in a directional container
        wrapper = ft.Container(
            content=bubble,
            padding=padding,
            alignment=ft.Alignment.CENTER_RIGHT if is_user else ft.Alignment.CENTER_LEFT
        )
        # Insert at index 0 so it appears at the bottom of the reversed list
        self.chat.controls.insert(0, wrapper)
        self.page.update()


class Display(DisplayInterface):

    def __init__(self, gui: GUI):
        self.gui = gui

    async def quit(self):
        await self.gui.page.window.destroy()
        os._exit(0)

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

    if engine.config.exists("ui.dark_mode"):
        page.theme_mode = ft.ThemeMode.DARK if engine.config.ui.dark_mode else ft.ThemeMode.LIGHT
    else:
        page.theme_mode = ft.ThemeMode.SYSTEM

    gui.initialize(display, engine)

    # Disable input while engine initializes
    await gui.disable_input()
    await engine.initialize()
    await gui.enable_input()

    page.update()

def run():
    ft.app(target=main)
