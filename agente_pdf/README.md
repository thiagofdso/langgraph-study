# PDF Analyzer Agent

This agent is designed to analyze PDF documents and extract specific information based on user queries. It utilizes the Gemini LLM to process PDF content (extracted as text) and provide structured responses.

## Functionality

- Extracts text content from PDF files using `PyPDFLoader`.
- Answers questions about PDF content, specifically focusing on deployment instructions for the Jaeger operator on OpenShift via the web console.
- Provides responses in Markdown format.

## Setup

Refer to the project's main `quickstart.md` for overall setup instructions.

## Usage

This agent is configured to process a specific PDF file (`openshift_container_platform-4.9-distributed_tracing-en-us.pdf`) and answer a predefined query ("como implantar o operator do jaeger usando web console do openshift") when executed. The PDF file is expected to be in the same directory as `main.py` or accessible via its path.

To run the PDF Analyzer Agent, simply execute the `main.py` script:

```bash
python agente_pdf/main.py
```

*(Note: Ensure the specified PDF file exists in the expected location.)*

## Expected Output

The agent will print a Markdown formatted response to the console, containing the instructions for deploying the Jaeger operator based on the PDF content.