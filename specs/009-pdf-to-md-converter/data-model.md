# Data Model: PDF to Markdown Converter

## Entities

### PDF Document

- **Description**: The input file that needs to be converted.
- **Attributes**:
    - `name`: `openshift_container_platform-4.9-distributed_tracing-en-us.pdf` (fixed)
    - `location`: Project root directory
    - `type`: Input

### Markdown Document

- **Description**: The output file generated after conversion.
- **Attributes**:
    - `name`: Derived from the input PDF name (e.g., `openshift_container_platform-4.9-distributed_tracing-en-us.md`)
    - `location`: `pdf_to_md` directory (relative to project root)
    - `type`: Output
