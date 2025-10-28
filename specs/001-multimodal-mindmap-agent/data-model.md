# Data Model for Multimodal Mindmap Agent

## Entities

### Multimodal Agent
- **Description**: An AI agent designed to process and understand various types of input, including images, to perform specific tasks.
- **Attributes**:
    - `input_image` (ImageFile): The image file provided for analysis.
    - `output_markdown` (str): The hierarchical markdown string generated from the image analysis.

### Mind Map Image
- **Description**: A digital image file (e.g., `folder_map.png`) that visually represents a mind map structure.
- **Attributes**:
    - `file_path` (str): The path to the image file.
    - `format` (str): The image file format (e.g., PNG).
    - `content_base64` (str): The base64 encoded string of the image content, used for multimodal LLM input.

### Hierarchical Markdown
- **Description**: A text string formatted using Markdown syntax to represent hierarchical data, typically using headings, lists, and indentation.
- **Attributes**:
    - `content` (str): The markdown formatted string.
    - `structure` (dict/json): (Optional) A programmatic representation of the hierarchical structure (e.g., nested dictionaries or lists) that the markdown is derived from.