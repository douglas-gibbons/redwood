import os
import google.generativeai as genai
import yaml
from rich.console import Console
from rich.markdown import Markdown

console = Console()

# Get API key from environment variable
GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")
genai.configure(api_key=GOOGLE_API_KEY)

# Load config file
with open("config.yaml", "r") as f:
    config = yaml.safe_load(f)

# Gemini model name
model_name = config["model"]["name"]

print(f"Using model: {model_name}")

model = genai.GenerativeModel(model_name)
chat = model.start_chat(history=[])

while True:
    val = input("> ")
    response = chat.send_message(val)
    console.print(response.text)
