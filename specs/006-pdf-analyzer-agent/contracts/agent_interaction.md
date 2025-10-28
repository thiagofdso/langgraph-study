# Agent Interaction Contract: PDF Analyzer Agent

## Agent Input

The agent expects a structured input that includes the PDF content and the user's query. This input will typically be provided programmatically to the agent's entry point.

### Input Structure

```json
{
  "pdf_path": "/path/to/your/document.pdf",
  "user_query": "How to deploy the Jaeger operator using the OpenShift web console?"
}
```

- **`pdf_path`**: (string, required) The absolute path to the PDF file that the agent needs to analyze. The agent will handle the conversion of this PDF to a Base64 encoded string internally.
- **`user_query`**: (string, required) The question or instruction from the user that the agent should answer based on the PDF's content.

## Agent Output

The agent will respond with a Markdown formatted string containing the answer to the user's query, derived from the analysis of the provided PDF.

### Output Structure

```markdown
# Jaeger Operator Deployment Steps

Here are the steps to deploy the Jaeger operator using the OpenShift web console, based on the provided PDF:

1. **Step 1**: Navigate to the OpenShift web console.
2. **Step 2**: Go to the Operators section.
3. **Step 3**: Search for "Jaeger Operator"...

...
```

- The output will be a single Markdown string.
- The content of the Markdown will directly address the `user_query` using information extracted from the `pdf_path`.

## LLM Interaction Format

The agent will construct a message to the LLM using the following format, incorporating the Base64 encoded PDF content:

```python
message = {
    "role": "user",
    "content": [
        {"type": "text", "text": user_query},
        {
            "type": "file",
            "base64": "[BASE64_ENCODED_PDF_STRING]",
            "mime_type": "application/pdf",
        },
    ]
}
```

- **`role`**: Always "user" for the initial query.
- **`content`**: A list containing:
    - A text object with the `user_query`.
    - A file object with the `base64` encoded PDF content and `mime_type` set to `application/pdf`.
