### Install Docling and Dependencies

Source: https://docling-project.github.io/docling/examples/serialization

Installs the docling library, docling-core, and rich for enhanced console output. This step is crucial for using Docling's serialization features. A kernel restart might be needed after installation.

```python
%pip install -qU pip docling docling-core~=2.29 rich
```

--------------------------------

### Troubleshoot Tesserocr Installation

Source: https://docling-project.github.io/docling/installation

These commands are used to uninstall and then reinstall the Tesserocr package with options that can help resolve common installation issues. The `--no-binary :all:` flag forces a source build.

```bash
pip uninstall tesserocr
pip install --no-binary :all: tesserocr
```

--------------------------------

### Set up Docling for Development

Source: https://docling-project.github.io/docling/installation

This command is used to set up the Docling project for development. It synchronizes dependencies, including all optional extras, ensuring all necessary components for contributing to the project are installed.

```bash
uv sync --all-extras
```

--------------------------------

### Install Docling Package

Source: https://docling-project.github.io/docling/installation

This command installs the Docling package using pip, the standard Python package manager. It is the primary method for getting Docling onto your system.

```bash
pip install docling
```

--------------------------------

### Install Dependencies for Docling and Qdrant

Source: https://docling-project.github.io/docling/examples/retrieval_qdrant

Installs the necessary Python packages for using Docling and Qdrant, including `qdrant-client`, `docling`, and `fastembed`. This step is crucial before proceeding with the rest of the setup.

```python
%pip install --no-warn-conflicts -q qdrant-client docling fastembed

```

--------------------------------

### Install Docling with CPU-only PyTorch for Linux

Source: https://docling-project.github.io/docling/installation

This command installs Docling with a specific PyTorch distribution optimized for CPU-only execution on Linux systems. It uses an extra index URL to fetch the correct PyTorch wheels.

```bash
# Example for installing on the Linux cpu-only version
pip install docling --extra-index-url https://download.pytorch.org/whl/cpu
```

--------------------------------

### Install Tesseract OCR on Debian-based Linux

Source: https://docling-project.github.io/docling/installation

This command installs Tesseract OCR and related development libraries on Debian-based Linux systems using `apt-get`. It also demonstrates how to determine and set the `TESSDATA_PREFIX` environment variable.

```bash
apt-get install tesseract-ocr tesseract-ocr-eng libtesseract-dev libleptonica-dev pkg-config
TESSDATA_PREFIX=$(dpkg -L tesseract-ocr-eng | grep tessdata$)
echo "Set TESSDATA_PREFIX=${TESSDATA_PREFIX}"
```

--------------------------------

### Install Tesseract OCR on RHEL-based Linux

Source: https://docling-project.github.io/docling/installation

This command installs Tesseract OCR and language packs on RHEL-based Linux systems using `dnf`. It also specifies the default `TESSDATA_PREFIX` path for RHEL systems.

```bash
dnf install tesseract tesseract-devel tesseract-langpack-eng tesseract-osd leptonica-devel
TESSDATA_PREFIX=/usr/share/tesseract/tessdata/
echo "Set TESSDATA_PREFIX=${TESSDATA_PREFIX}"
```

--------------------------------

### Install LangChain Docling and Dependencies

Source: https://docling-project.github.io/docling/examples/rag_langchain

Installs the required Python packages for LangChain Docling, LangChain core, Hugging Face integration, Milvus integration, and dotenv. This command is essential for setting up the environment to run the example.

```shell
%pip install -q --progress-bar off --no-warn-conflicts langchain-docling langchain-core langchain-huggingface langchain_milvus langchain python-dotenv

```

--------------------------------

### Install Flash Attention Package

Source: https://docling-project.github.io/docling/faq

These shell commands provide two methods for installing the Flash Attention package. The first builds from source, requiring a CUDA development environment. The second uses pre-built wheels, which may not be available for all setups.

```shell
# Building from sources (required the CUDA dev environment)
pip install flash-attn
```

```shell
# Using pre-built wheels (not available in all possible setups)
FLASH_ATTENTION_SKIP_CUDA_BUILD=TRUE pip install flash-attn
```

--------------------------------

### Install Docling on macOS Intel with Compatible PyTorch

Source: https://docling-project.github.io/docling/installation

This section provides commands for installing Docling on macOS Intel (x86_64) systems, specifically addressing potential PyTorch compatibility issues with newer versions. It offers options for `uv`, `pip`, and `poetry` package managers.

```bash
# For uv users
uv add torch==2.2.2 torchvision==0.17.2 docling

# For pip users
pip install "docling[mac_intel]"

# For Poetry users
poetry add docling
```

--------------------------------

### Install Tesseract OCR on macOS

Source: https://docling-project.github.io/docling/installation

This command installs Tesseract and its dependencies on macOS using Homebrew. It also shows how to set the `TESSDATA_PREFIX` environment variable, which is required for Tesseract to locate its language files.

```bash
brew install tesseract leptonica pkg-config
TESSDATA_PREFIX=/opt/homebrew/share/tessdata/
echo "Set TESSDATA_PREFIX=${TESSDATA_PREFIX}"
```

--------------------------------

### Install ocrmac for macOS OCR

Source: https://docling-project.github.io/docling/installation

This command installs the `ocrmac` package, which utilizes Apple's Vision or LiveText framework for OCR. This is a system dependency for using the OcrMac engine with Docling on macOS.

```bash
pip install ocrmac
```

--------------------------------

### Install Docling and Transformers

Source: https://docling-project.github.io/docling/examples/hybrid_chunking

Installs the necessary libraries: pip, docling, and transformers. It's recommended to restart the kernel after installation to ensure updated packages are used.

```python
%pip install -qU pip docling transformers

```

--------------------------------

### Set Up VlmPipeline Options for Document Conversion

Source: https://docling-project.github.io/docling/examples/compare_vlm_models

Initializes and configures `VlmPipelineOptions` for document conversion, with an option to generate page images. It also includes commented-out settings for enabling flash attention on GPU systems.

```python
pipeline_options = VlmPipelineOptions()
pipeline_options.generate_page_images = True

## On GPU systems, enable flash_attention_2 with CUDA:
# pipeline_options.accelerator_options.device = AcceleratorDevice.CUDA
# pipeline_options.accelerator_options.cuda_use_flash_attention2 = True
```

--------------------------------

### Configure Raw Prompt VLM Options for Transformers

Source: https://docling-project.github.io/docling/examples/compare_vlm_models

Configures VLM options for using a raw prompt with the Dolphin model via the Transformers framework. This is presented as a non-standard usage example to demonstrate raw prompt input, specifying model details and inference parameters.

```python
dolphin_oneshot = InlineVlmOptions(
        repo_id="ByteDance/Dolphin",
        prompt="<s>Read text in the image. <Answer/>",
        response_format=ResponseFormat.MARKDOWN,
        inference_framework=InferenceFramework.TRANSFORMERS,
        transformers_model_type=TransformersModelType.AUTOMODEL_IMAGETEXTTOTEXT,
        transformers_prompt_style=TransformersPromptStyle.RAW,
        supported_devices=[AcceleratorDevice.CUDA, AcceleratorDevice.CPU],
        scale=2.0,
        temperature=0.0,
    )
```

--------------------------------

### Install DPK Transforms and Dependencies

Source: https://docling-project.github.io/docling/examples/dpk-ingest-chunk-tokenize

Installs the Data Prep Kit (DPK) library with specific transforms for Docling2Parquet, Doc_Chunk, and Tokenization, along with pandas and a compatible version of numpy. It also loads environment variables from a .env file, which are necessary for accessing external APIs.

```python
%%capture
%pip install "data-prep-toolkit-transforms[docling2parquet,doc_chunk,tokenization]"
%pip install pandas
%pip install "numpy<2.0"
from dotenv import load_dotenv

load_dotenv(".env", override=True)
```

--------------------------------

### Python Docling Indexing Pipeline Setup and Run

Source: https://docling-project.github.io/docling/examples/rag_haystack

This snippet demonstrates the complete setup and execution of an indexing pipeline using Docling, Haystack, and Milvus. It initializes the document store, adds components like DoclingConverter and SentenceTransformersDocumentEmbedder, connects them based on export type, and runs the pipeline. Dependencies include 'docling_haystack', 'haystack', and 'milvus_haystack'. The input is a set of file paths, and the output is a dictionary indicating the number of documents written.

```python
from docling_haystack.converter import DoclingConverter
from haystack import Pipeline
from haystack.components.embedders import (
    SentenceTransformersDocumentEmbedder,
    SentenceTransformersTextEmbedder,
)
from haystack.components.preprocessors import DocumentSplitter
from haystack.components.writers import DocumentWriter
from milvus_haystack import MilvusDocumentStore, MilvusEmbeddingRetriever

from docling.chunking import HybridChunker

document_store = MilvusDocumentStore(
    connection_args={"uri": MILVUS_URI},
    drop_old=True,
    text_field="txt",  # set for preventing conflict with same-name metadata field
)

idx_pipe = Pipeline()
idx_pipe.add_component(
    "converter",
    DoclingConverter(
        export_type=EXPORT_TYPE,
        chunker=HybridChunker(tokenizer=EMBED_MODEL_ID),
    ),
)
idx_pipe.add_component(
    "embedder",
    SentenceTransformersDocumentEmbedder(model=EMBED_MODEL_ID),
)
idx_pipe.add_component("writer", DocumentWriter(document_store=document_store))
if EXPORT_TYPE == ExportType.DOC_CHUNKS:
    idx_pipe.connect("converter", "embedder")
elif EXPORT_TYPE == ExportType.MARKDOWN:
    idx_pipe.add_component(
        "splitter",
        DocumentSplitter(split_by="sentence", split_length=1),
    )
    idx_pipe.connect("converter.documents", "splitter.documents")
    idx_pipe.connect("splitter.documents", "embedder.documents")
else:
    raise ValueError(f"Unexpected export type: {EXPORT_TYPE}")
idx_pipe.connect("embedder", "writer")
idx_pipe.run({"converter": {"paths": PATHS}})

```

--------------------------------

### Install LangChain Docling and Dependencies

Source: https://docling-project.github.io/docling/examples/visual_grounding

Installs essential Python packages for LangChain, Docling, Milvus, Hugging Face, and Matplotlib. Use `--no-warn-conflicts` for Colab environments. A kernel restart may be required after installation.

```python
%pip install -q --progress-bar off --no-warn-conflicts langchain-docling langchain-core langchain-huggingface langchain_milvus langchain matplotlib python-dotenv

```

--------------------------------

### Set up DocumentConverter for PDF and Image Inputs

Source: https://docling-project.github.io/docling/examples/compare_vlm_models

Initializes a `DocumentConverter` with specific format options for PDF and IMAGE inputs. Each input format is configured to use `VlmPipeline` with the provided `pipeline_options` for processing.

```python
converter = DocumentConverter(
            format_options={
                InputFormat.PDF: PdfFormatOption(
                    pipeline_cls=VlmPipeline,
                    pipeline_options=pipeline_options,
                ),
                InputFormat.IMAGE: PdfFormatOption(
                    pipeline_cls=VlmPipeline,
                    pipeline_options=pipeline_options,
                ),
            },
        )
```

--------------------------------

### Setup Experiment Folders and Article List

Source: https://docling-project.github.io/docling/examples/dpk-ingest-chunk-tokenize

Initializes the experiment by creating a temporary directory for data storage and defining a list of articles to be processed. It then calls the `load_corpus` function to download the specified articles into the created data folder and asserts that at least one document was successfully downloaded.

```python
import os
import tempfile

datafolder = tempfile.mkdtemp(dir=os.getcwd())
articles = ["Science,_technology,_engineering,_and_mathematics"]
assert load_corpus(articles, datafolder) > 0, "Faild to download any documents"
```

--------------------------------

### Import Docling Core Types and Pipeline Options

Source: https://docling-project.github.io/docling/examples/translate

Imports necessary modules and types from the Docling library for PDF conversion and pipeline configuration. It sets up logging and defines a constant for image resolution scaling.

```python
import logging
from pathlib import Path

from docling_core.types.doc import ImageRefMode, TableItem, TextItem

from docling.datamodel.base_models import InputFormat
from docling.datamodel.pipeline_options import PdfPipelineOptions
from docling.document_converter import DocumentConverter, PdfFormatOption

_log = logging.getLogger(__name__)

IMAGE_RESOLUTION_SCALE = 2.0

```

--------------------------------

### Install Dependencies for RAG

Source: https://docling-project.github.io/docling/examples/rag_milvus

Installs necessary Python packages for RAG functionality, including pymilvus, docling, openai, and torch. This is a prerequisite for running the notebook.

```bash
! pip install --upgrade pymilvus docling openai torch

```

--------------------------------

### Register Docling Plugin with setup.cfg

Source: https://docling-project.github.io/docling/concepts/plugins

This configuration example illustrates how to declare a Docling plugin entry point within a setup.cfg file. It uses the `[options.entry_points]` section to map a plugin name to its Python module, allowing setuptools to discover and load the plugin.

```ini
[options.entry_points]
docling =
    your_plugin_name = your_package.module

```

--------------------------------

### Configure Docling Parse with EasyOCR on CPU

Source: https://docling-project.github.io/docling/examples/custom_convert

This example shows how to configure Docling's parser with EasyOCR, specifically forcing it to run on the CPU. This is useful for environments where GPU is not available or desired. It enables OCR and table structure detection.

```python
pipeline_options = PdfPipelineOptions()
pipeline_options.do_ocr = True
pipeline_options.ocr_options.use_gpu = False
pipeline_options.do_table_structure = True
pipeline_options.table_structure_options.do_cell_matching = True
doc_converter = DocumentConverter(
    format_options={
        InputFormat.PDF: PdfFormatOption(pipeline_options=pipeline_options)
    }
)
```

--------------------------------

### Install Docling and Weaviate Client Libraries

Source: https://docling-project.github.io/docling/examples/rag_weaviate

Installs the required Python libraries for Docling, Weaviate client, rich, and PyTorch. It also suppresses verbose logging from the Weaviate client and general warnings. This step is crucial before proceeding with the rest of the notebook.

```python
%%capture
%pip install docling~="2.7.0"
%pip install -U weaviate-client~="4.9.4"
%pip install rich
%pip install torch

import logging
import warnings

warnings.filterwarnings("ignore")

# Suppress Weaviate client logs
logging.getLogger("weaviate").setLevel(logging.ERROR)
```

--------------------------------

### Install Docling with VLM support

Source: https://docling-project.github.io/docling/examples/pictures_description

Installs the docling library with VLM (Vision-Language Model) capabilities and ipython for interactive environments. This is a prerequisite for using local VLMs with docling.

```shell
%pip install -q docling[vlm] ipython
```

--------------------------------

### Install Docling with VLM Support

Source: https://docling-project.github.io/docling/examples/extraction

Installs the Docling package with Visual Language Model (VLM) support. This is a prerequisite for using certain advanced features of Docling.

```shell
%pip install -q docling[vlm]  # Install the Docling package with VLM support

```

--------------------------------

### Define Document Source and Excerpt Cues

Source: https://docling-project.github.io/docling/examples/serialization

Sets the source URL for the document to be processed and defines start and stop cues. These cues help in extracting a specific portion of the document for display or further processing, useful for managing output length.

```python
DOC_SOURCE = "https://arxiv.org/pdf/2311.18481"

# we set some start-stop cues for defining an excerpt to print
start_cue = "Copyright © 2024"
stop_cue = "Application of NLP to ESG"
```

--------------------------------

### Configure Docling Parse with Tesseract CLI

Source: https://docling-project.github.io/docling/examples/custom_convert

This snippet demonstrates using Docling's parser with the Tesseract OCR engine via its command-line interface (CLI). It enables OCR and table structure detection. This requires Tesseract to be installed and configured in the system's PATH.

```python
pipeline_options = PdfPipelineOptions()
pipeline_options.do_ocr = True
pipeline_options.do_table_structure = True
pipeline_options.table_structure_options.do_cell_matching = True
pipeline_options.ocr_options = TesseractCliOcrOptions()
doc_converter = DocumentConverter(
    format_options={
        InputFormat.PDF: PdfFormatOption(pipeline_options=pipeline_options)
    }
)
```

--------------------------------

### Python: Convert single source to Markdown with Docling

Source: https://docling-project.github.io/docling/examples/minimal

This snippet demonstrates how to use the Docling library to convert a single document source, specified by a URL or local file path, into a unified Docling document. The converted document is then exported to Markdown format and printed to standard output. It requires Python 3.9+ and the 'docling' package to be installed. The converter automatically detects various file formats.

```python
from docling.document_converter import DocumentConverter

# Change this to a local path or another URL if desired.
# Note: using the default URL requires network access; if offline, provide a
# local file path (e.g., Path("/path/to/file.pdf")).
source = "https://arxiv.org/pdf/2408.09869"

converter = DocumentConverter()
result = converter.convert(source)

# Print Markdown to stdout.
print(result.document.export_to_markdown())

```

--------------------------------

### Install Dependencies with uv

Source: https://docling-project.github.io/docling/examples/rag_opensearch

Installs necessary Python packages for the RAG notebook using the 'uv' package manager. This ensures all required libraries for Docling, LlamaIndex, OpenSearch, and Ollama are available in the virtual environment.

```bash
curl -LsSf https://astral.sh/uv/install.sh | sh

uv venv
source .venv/bin/activate

! uv pip install -q --no-progress notebook ipywidgets docling llama-index-readers-file llama-index-readers-docling llama-index-node-parser-docling llama-index-vector-stores-opensearch llama-index-embeddings-ollama llama-index-llms-ollama
```

--------------------------------

### Configure DocumentConverter with Tesseract OCR

Source: https://docling-project.github.io/docling/installation

This Python code snippet demonstrates how to configure the `DocumentConverter` to use the Tesseract OCR engine. It involves setting `do_ocr` to True and specifying `TesseractOcrOptions` for the `ocr_options`.

```python
from docling.datamodel.base_models import ConversionStatus, PipelineOptions
from docling.datamodel.pipeline_options import PipelineOptions, EasyOcrOptions, TesseractOcrOptions
from docling.document_converter import DocumentConverter

pipeline_options = PipelineOptions()
pipeline_options.do_ocr = True
pipeline_options.ocr_options = TesseractOcrOptions()  # Use Tesseract

doc_converter = DocumentConverter(
    pipeline_options=pipeline_options,
)
```

--------------------------------

### Serialize Document to Markdown with Image Placeholders

Source: https://docling-project.github.io/docling/examples/serialization

This Python code snippet demonstrates how to initialize and use the MarkdownDocSerializer to convert a document into Markdown format. It configures the serializer to use placeholder images and extracts a specific section of the serialized text based on start and stop cues. Dependencies include the Docling library components like MarkdownDocSerializer, AnnotationPictureSerializer, MarkdownParams, and ImageRefMode.

```python
serializer = MarkdownDocSerializer(
    doc=doc,
    picture_serializer=AnnotationPictureSerializer(),
    params=MarkdownParams(
        image_mode=ImageRefMode.PLACEHOLDER,
        image_placeholder="",
    ),
)
ser_result = serializer.serialize()
ser_text = ser_result.text

print_in_console(ser_text[ser_text.find(start_cue) : ser_text.find(stop_cue)])

```

--------------------------------

### Python: Set up and use DocumentConverter with PDF input

Source: https://docling-project.github.io/docling/examples/translate

Demonstrates how to initialize the DocumentConverter for PDF input, configure pipeline options for image generation and scaling, and convert a PDF document to a Markdown format. It highlights the importance of preserving page images for further processing.

```python
import logging
from pathlib import Path
from docling_core.types.doc import ImageRefMode, TableItem, TextItem
from docling.datamodel.base_models import InputFormat
from docling.datamodel.pipeline_options import PdfPipelineOptions
from docling.document_converter import DocumentConverter, PdfFormatOption

_log = logging.getLogger(__name__)
IMAGE_RESOLUTION_SCALE = 2.0

def main():
    logging.basicConfig(level=logging.INFO)
    data_folder = Path(__file__).parent / "../../tests/data"
    input_doc_path = data_folder / "pdf/2206.01062.pdf"
    output_dir = Path("scratch")

    pipeline_options = PdfPipelineOptions()
    pipeline_options.images_scale = IMAGE_RESOLUTION_SCALE
    pipeline_options.generate_page_images = True
    pipeline_options.generate_picture_images = True

    doc_converter = DocumentConverter(
        format_options={
            InputFormat.PDF: PdfFormatOption(pipeline_options=pipeline_options)
        }
    )

    conv_res = doc_converter.convert(input_doc_path)
    doc_filename = conv_res.input.file.name

    md_filename = output_dir / f"{doc_filename}-with-images-orig.md"
    conv_doc.save_as_markdown(md_filename, image_mode=ImageRefMode.EMBEDDED)

if __name__ == "__main__":
    main()
```