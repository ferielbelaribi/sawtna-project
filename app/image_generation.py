import requests
from PIL import Image
from io import BytesIO
import urllib.parse
import time

def generate_image(prompt, width=1024, height=1024, seed=None):
    encoded_prompt = urllib.parse.quote(prompt)
    url = f"https://image.pollinations.ai/prompt/{encoded_prompt}?width={width}&height={height}&nologo=true"
    if seed:
        url += f"&seed={seed}"
    response = requests.get(url, timeout=60)
    response.raise_for_status()
    img = Image.open(BytesIO(response.content))
    timestamp = int(time.time())
    filename = f"generated_image_{timestamp}.png"
    img.save(filename)
    return filename

def generate_image_bytes(prompt, width=1024, height=1024, seed=None):
    """Return image bytes instead of saving to disk"""
    encoded_prompt = urllib.parse.quote(prompt)
    url = f"https://image.pollinations.ai/prompt/{encoded_prompt}?width={width}&height={height}&nologo=true"
    if seed:
        url += f"&seed={seed}"
    response = requests.get(url, timeout=60)
    response.raise_for_status()
    return response.content
