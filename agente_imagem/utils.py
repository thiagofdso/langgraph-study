import base64
import io
from PIL import Image

def image_to_base64(image_path):
    with open(image_path, "rb") as image_file:
        encoded_string = base64.b64encode(image_file.read()).decode('utf-8')
    return encoded_string

def base64_to_image(base64_string, output_path="decoded_image.png"):
    img_bytes = base64.b64decode(base64_string)
    with open(output_path, "wb") as f:
        f.write(img_bytes)
    return output_path
