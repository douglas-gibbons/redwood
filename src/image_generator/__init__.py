import os
import io
import logging
from google import genai
from google.genai import types
from PIL import Image
from mcp.server.fastmcp import FastMCP
from config import Config
import sys
import argparse

logging.getLogger().handlers.clear()
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.WARNING,
)

parser = argparse.ArgumentParser()
parser.add_argument("--model", type=str, default="imagen-4.0-fast-generate-001")
parser.add_argument("--output-dir", type=str, default="~/Downloads", help="Directory where images will be saved")
args, unknown = parser.parse_known_args()

IMAGE_MODEL = args.model
OUTPUT_DIR = os.path.expanduser(args.output_dir)
sys.argv = [sys.argv[0]] + unknown

mcp = FastMCP(name="image_generator")

@mcp.tool()
def generate_image(prompt: str, filename: str = "generated_image.jpg") -> str:
    """
    Generates an image from a text prompt and saves it locally.
    
    Args:
        prompt: A descriptive prompt for the image to generate.
        filename: The filename to save the image as.
    """
    config = Config()
    if not config.exists("model.api_key"):
        return "Error: API Key missing from configuration"
        
    client = genai.Client(api_key=config.model.api_key)

    try:
        response = client.models.generate_content(
            model=IMAGE_MODEL,
            contents=[prompt],
        )

        for part in response.parts:
            if part.inline_data is not None:
                os.makedirs(str(OUTPUT_DIR), exist_ok=True)
                full_path = os.path.join(str(OUTPUT_DIR), str(filename))

                image = part.as_image()
                image.save(full_path)
                return f"Image successfully generated and saved as {full_path}"
        return "No images were generated."
    except Exception as e:
        return f"An error occurred during image generation: {e}"

def run():
    mcp.run()

if __name__ == "__main__":
    run()
