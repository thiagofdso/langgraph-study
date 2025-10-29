# Quickstart: PDF to Markdown Converter

This guide provides instructions to quickly set up and run the PDF to Markdown converter.

## Prerequisites

- Python 3.11 or higher

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

    The `docling` library is required. Ensure it's added to your `requirements.txt` and installed.

    ```bash
    # Add docling to requirements.txt if not present
    echo "docling" >> requirements.txt
    pip install -r requirements.txt
    ```

4.  **Create the `pdf_to_md` directory and `main.py` file**:

    ```bash
    mkdir -p pdf_to_md
    touch pdf_to_md/main.py
    ```

5.  **Place the PDF file**:

    Ensure the PDF file `openshift_container_platform-4.9-distributed_tracing-en-us.pdf` is located in the project root directory.

## Usage

To run the converter, execute the `main.py` script from the project root:

```bash
python pdf_to_md/main.py
```

Upon successful execution, a Markdown file (e.g., `openshift_container_platform-4.9-distributed_tracing-en-us.md`) will be created in the `pdf_to_md` directory.
