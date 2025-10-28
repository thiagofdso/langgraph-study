# Quickstart: PDF Analyzer Agent

This guide provides instructions to quickly set up and run the PDF Analyzer Agent.

## Prerequisites

- Python 3.11 installed.
- `venv` for virtual environment management.
- Access to a Google Gemini API key with `gemini-2.5-flash` model access.

## Setup

1.  **Clone the repository** (if you haven't already):

    ```bash
    git clone <repository_url>
    cd langgraph
    ```

2.  **Create and activate a virtual environment**:

    ```bash
    python3.11 -m venv venv
    source venv/bin/activate
    ```

3.  **Install dependencies**:

    ```bash
    pip install -r requirements.txt
    ```

4.  **Configure environment variables**:

    Copy the `.env.example` from `agente_simples` (or create a new `.env` file) and add your Google Gemini API key:

    ```ini
    # .env
    GOOGLE_API_KEY="your_gemini_api_key_here"
    ```

## Running the Agent

To run the PDF Analyzer Agent, you will need a PDF file. For this example, we'll assume you have `openshift_container_platform-4.9-distributed_tracing-en-us.pdf` in a known location.

1.  **Place your PDF file**:

    Ensure the PDF file you want to analyze (e.g., `openshift_container_platform-4.9-distributed_tracing-en-us.pdf`) is accessible from your project directory. For simplicity, you might place it in the `agente_pdf/` directory or provide its absolute path.

2.  **Execute the agent**:

    Navigate to the `agente_pdf` directory and run the `main.py` script, providing the path to your PDF and your query:

    ```bash
    cd agente_pdf
    python main.py --pdf_path "/path/to/your/openshift_container_platform-4.9-distributed_tracing-en-us.pdf" --query "How to deploy the Jaeger operator using the OpenShift web console?"
    ```

    *(Note: The `main.py` script will need to be implemented to accept these arguments and process the PDF as described in the plan.)*

## Expected Output

The agent will print a Markdown formatted response to the console, containing the instructions for deploying the Jaeger operator based on the PDF content.
