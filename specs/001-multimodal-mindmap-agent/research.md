# Research for Multimodal Mindmap Agent

## Extracting Data from PNG files in Base64 (Python)

-   **Decision**: Use Python's built-in `base64` module to encode/decode base64 strings and the `Pillow` library for image processing. For extracting text from the image (if needed for mind map analysis), `pytesseract` (OCR) can be considered.
-   **Rationale**: `base64` module is standard for base64 encoding/decoding. `Pillow` is a widely used and robust image processing library in Python. OCR is necessary if the mind map content is not directly accessible as text.
-   **Alternatives considered**: Other image processing libraries (e.g., OpenCV) but Pillow is sufficient for basic image handling.

**Example Code for Base64 Encoding/Decoding and Image Handling**:

```python
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

# Example usage:
# encoded_image = image_to_base64("folder_map.png")
# decoded_image_path = base64_to_image(encoded_image)
# print(f"Decoded image saved to: {decoded_image_path}")

# To open and process with Pillow:
# img = Image.open(decoded_image_path)
# img.show() # To display the image
```

## Langchain Multimodal Messages

-   **Decision**: Use `HumanMessage` with multimodal content (text and image) to send the image to the `gemini-2.5-flash` model.
-   **Rationale**: LangChain messages standardize communication with models, and `HumanMessage` supports multimodal content, which is essential for sending images to models like Gemini.
-   **Alternatives considered**: None, as `HumanMessage` is the standard way to send user input, including multimodal, in LangChain.

**Example Code for Langchain Multimodal Message**:

```python

# Assuming 'base64' is the base64 encoded string of the image
# and 'prompt_text' is the text instruction for the model.

# From base64 data
message = {
    "role": "user",
    "content": [
        {"type": "text", "text": "Analyze this mind map and extract its hierarchical structure in markdown."},
        {
            "type": "image",
            "base64": "AAAAIGZ0eXBtcDQyAAAAAGlzb21tcDQyAAACAGlzb2...",
            "mime_type": "image/jpeg",
        },
    ]
}
# This message can then be passed to a LangChain LLM or agent.
```