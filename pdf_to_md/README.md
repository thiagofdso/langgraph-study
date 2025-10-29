# PDF to Markdown Converter

This project contains a Python script to convert a PDF file to a Markdown file using the `docling` library.

## Prerequisites

- Python 3.11 or higher
- `docling` library and other dependencies from `requirements.txt`

## Setup

1.  **Navigate to the project root directory**:

    ```bash
    cd /path/to/your/langgraph/project
    ```

2.  **Create and activate a virtual environment** (if you haven't already):

    ```bash
    python3.11 -m venv venv
    source venv/bin/activate
    ```

3.  **Install dependencies**:

    ```bash
    pip install -r requirements.txt
    ```

4.  **Place the PDF file**:

    Ensure the PDF file `openshift_container_platform-4.9-distributed_tracing-en-us.pdf` is located in the project root directory.

## Usage

To run the converter, execute the `main.py` script from the project root:

```bash
python pdf_to_md/main.py
```

Upon successful execution, a Markdown file (`openshift_container_platform-4.9-distributed_tracing-en-us.md`) will be created in the `pdf_to_md` directory.
