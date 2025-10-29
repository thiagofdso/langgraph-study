# This script converts a specific PDF file to a Markdown file using the docling library.
import sys
from pathlib import Path
from docling.document_converter import DocumentConverter

def main():
    """
    Converts a specific PDF file to a Markdown file.
    """
    # Configure the fixed input PDF path
    input_pdf_path = Path("/root/code/langgraph/openshift_container_platform-4.9-distributed_tracing-en-us.pdf")
    output_dir = Path("/root/code/langgraph/pdf_to_md")

    # Add basic error handling
    if not input_pdf_path.is_file():
        print(f"Error: Input PDF file not found at '{input_pdf_path}'")
        sys.exit(1)

    try:
        # Implement PDF to Markdown conversion logic
        print(f"Starting conversion of '{input_pdf_path.name}'...")
        converter = DocumentConverter()
        result = converter.convert(input_pdf_path)
        markdown_content = result.document.export_to_markdown()
        print("Conversion successful.")

        # Save the generated Markdown content
        output_filename = input_pdf_path.stem + ".md"
        output_md_path = output_dir / output_filename
        
        print(f"Saving Markdown to '{output_md_path}'...")
        output_md_path.write_text(markdown_content, encoding='utf-8')
        print("Markdown file saved successfully.")

    except Exception as e:
        print(f"An unexpected error occurred: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()