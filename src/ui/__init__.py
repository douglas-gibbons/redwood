import asyncio
import threading
import logging
import tkinter as tk
from tkinter import scrolledtext
from chat_engine.chat_engine import ChatEngine
from chat_engine.display_interface import DisplayInterface

logger = logging.getLogger(__name__)


class RedwoodUI(DisplayInterface):
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
        self.user_input.bind("<Return>", self.send_message)
        
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
        
        # State for blocking input
        self.input_ready_event = threading.Event()
        self.input_value = ""
        
        # Background thread for the ChatEngine
        self.thread = threading.Thread(target=self.run_engine, daemon=True)
        self.thread.start()

    def run_engine(self):
        """Runs the async ChatEngine in the background thread."""
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        engine = ChatEngine(self)
        loop.run_until_complete(engine.engine())

    # DisplayInterface Implementation

    def info(self, message):
        self.append_to_chat("System", message)

    def warn(self, message):
        self.append_to_chat("Warning", message)

    def error(self, message):
        self.append_to_chat("Error", message)

    def markdown(self, prompt):
        self.append_to_chat("Redwood", prompt)
        return prompt

    def input(self):
        """Blocks the background thread until input is ready from the UI."""
        self.root.after(0, lambda: self.set_input_state('normal'))
        self.input_ready_event.wait()
        self.input_ready_event.clear()
        self.root.after(0, lambda: self.set_input_state('disabled'))
        return self.input_value

    # UI Helpers

    def set_input_state(self, state):
        self.user_input.config(state=state)
        self.send_button.config(state=state)
        if state == 'normal':
            self.user_input.focus()

    def append_to_chat(self, sender, message):
        def _append():
            self.chat_display.config(state='normal')
            self.chat_display.insert(tk.END, f"{sender}:\n{message}\n\n")
            self.chat_display.see(tk.END)
            self.chat_display.config(state='disabled')
        self.root.after(0, _append)

    def send_message(self, event=None):
        text = self.user_input.get().strip()
        if not text:
            return
        self.user_input.delete(0, tk.END)
        self.append_to_chat("You", text)
        self.input_value = text
        self.input_ready_event.set()

    def cmd_tools(self):
        self.user_input.delete(0, tk.END)
        self.user_input.insert(0, "/tools")
        self.send_message()

    def cmd_locate(self):
        self.user_input.delete(0, tk.END)
        self.user_input.insert(0, "/locate")
        self.send_message()

    def cmd_reset(self):
        self.user_input.delete(0, tk.END)
        self.user_input.insert(0, "/reset")
        self.send_message()

def run():
    root = tk.Tk()
    app = RedwoodUI(root)
    root.mainloop()

if __name__ == "__main__":
    run()
