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
        response = client.models.generate_images(
            model=IMAGE_MODEL,
            prompt=prompt,
            config=types.GenerateImagesConfig(
                number_of_images=1,
                output_mime_type="image/jpeg",
                aspect_ratio="1:1"
            )
        )

        if response.generated_images:
            image_bytes = response.generated_images[0].image.image_bytes
            pil_image = Image.open(io.BytesIO(image_bytes))
            
            os.makedirs(str(OUTPUT_DIR), exist_ok=True)
            full_path = os.path.join(str(OUTPUT_DIR), str(filename))
            pil_image.save(full_path)
            return f"Image successfully generated and saved as {full_path}"
        else:
            return "No images were generated."
    except Exception as e:
        return f"An error occurred during image generation: {e}"

def run():
    mcp.run()

if __name__ == "__main__":
    run()
