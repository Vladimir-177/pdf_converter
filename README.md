# PDF to Markdown Converter

A Python utility for converting PDF and DOCX documents to Markdown format using [Docling](https://github.com/DS4SD/docling), with support for document structure analysis and article-based splitting.

## Features

- **PDF/DOCX to Markdown conversion** with configurable OCR and table structure preservation
- **Document structure analysis** with hierarchical item iteration
- **Contract/document splitting** by article sections using regex patterns
- **JSON export** of document structure for further processing
- **Type hints** and comprehensive error handling for production use
- **Logging support** for debugging and monitoring

## Project Structure

```
pdf_converter/
├── README.md                           # This file
├── pdf_to_md2.py                       # Main conversion utilities (based on IBM docling)
├── pdf_to_md.py                        # Simple alternative conversion script (based on MS markitdown)
├── pdf_to_md3.py                       # Resource-intensive additional conversion script (based on  marker-pdf)
└── data/
    ├── sample A101-2017 (90 pages).pdf # Sample AIA contract document
    ├── sample a101-2017_exhibit_A.pdf  # Sample contract exhibit
    └── output/
        ├── sample A101-2017 (90 pages).md   # Converted markdown
        ├── sample A101-2017 (90 pages).json # Document structure
        ├── sample a101-2017_exhibit_A.md    # Converted exhibit
        └── sample a101-2017_exhibit_A.json  # Exhibit structure
```

## Installation

### Prerequisites

- Python 3.10+
- Virtual environment (recommended)

### Setup

```bash
# Create virtual environment
python3 -m venv .venv

# Activate virtual environment
source .venv/bin/activate  # macOS/Linux
# or
.venv\Scripts\activate  # Windows

# Create required directories
mkdir -p data/output

# Install dependencies
pip install docling
```

## Usage

### Basic Usage: Convert PDF to Markdown

```python
from pdf_to_md2 import convert_to_markdown_by_docling, save_markdown, save_structure_as_json
from pathlib import Path

# Convert PDF to document object
input_pdf = Path("./data/sample A101-2017 (90 pages).pdf")
document = convert_to_markdown_by_docling(input_pdf)

# Export to Markdown
markdown_content = document.export_to_markdown()
with open("output.md", "w", encoding="utf-8") as f:
    f.write(markdown_content)

# Export structure as JSON
document_dict = document.export_to_dict()
with open("output.json", "w") as f:
    import json
    json.dump(document_dict, f, indent=2)
```

### Advanced Usage: Custom OCR and Table Settings

```python
from pdf_to_md2 import convert_to_markdown_by_docling

# Enable OCR for scanned PDFs
document = convert_to_markdown_by_docling(
    "./data/sample.pdf",
    do_ocr=True,
    do_table_structure=True
)

# Reuse converter instance for multiple files
from docling.document_converter import DocumentConverter

converter = DocumentConverter()
doc1 = convert_to_markdown_by_docling("file1.pdf", converter=converter)
doc2 = convert_to_markdown_by_docling("file2.pdf", converter=converter)
```

### Document Structure Analysis

```python
from pdf_to_md2 import print_structure, split_contract_by_article
from docling_core.types.doc.labels import DocItemLabel

# Print document structure (articles and sections)
print_structure(document)

# Split markdown by article sections
split_contract_by_article("./data/output/sample A101-2017 (90 pages).md")
```

### Complete Example: Full Pipeline

```python
import logging
from pathlib import Path
from pdf_to_md2 import (
    convert_to_markdown_by_docling,
    save_markdown,
    save_structure_as_json,
    print_structure,
    split_contract_by_article
)

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

def main():
    input_pdf = Path("./data/sample A101-2017 (90 pages).pdf")
    output_dir = Path("./data/output/")
    output_dir.mkdir(parents=True, exist_ok=True)

    # 1. Convert PDF to document
    print("Converting PDF to document...")
    try:
        document = convert_to_markdown_by_docling(
            input_pdf,
            do_ocr=False,
            do_table_structure=True
        )
    except FileNotFoundError as e:
        print(f"Error: {e}")
        return
    except RuntimeError as e:
        print(f"Conversion failed: {e}")
        return

    # 2. Save markdown
    print("Exporting to Markdown...")
    markdown_content = document.export_to_markdown()
    md_path = output_dir / f"{input_pdf.stem}.md"
    with open(md_path, "w", encoding="utf-8") as f:
        f.write(markdown_content)

    # 3. Save structure as JSON
    print("Saving document structure...")
    json_path = output_dir / f"{input_pdf.stem}.json"
    structure = document.export_to_dict()
    import json
    with open(json_path, "w") as f:
        json.dump(structure, f, indent=2)

    # 4. Analyze structure
    print("\nDocument Structure:")
    print_structure(document)

    # 5. Split by articles
    print("\n\nArticles Found:")
    split_contract_by_article(str(md_path))

    print(f"\n✓ Conversion complete!")
    print(f"  - Markdown: {md_path}")
    print(f"  - Structure: {json_path}")

if __name__ == "__main__":
    main()
```

## API Reference

### `convert_to_markdown_by_docling()`

Converts a PDF or DOCX document to a Docling Document object.

**Parameters:**
- `input_file` (str | Path): Path to the input PDF or DOCX file
- `do_ocr` (bool, default=False): Enable OCR for scanned documents
- `do_table_structure` (bool, default=True): Attempt to preserve table structure
- `converter` (Optional[DocumentConverter], default=None): Reuse an existing converter instance

**Returns:** Docling document object with export methods

**Raises:**
- `FileNotFoundError`: If input file does not exist
- `RuntimeError`: If conversion fails

**Example:**
```python
doc = convert_to_markdown_by_docling("contract.pdf", do_ocr=False)
```

### `save_markdown()`

Saves markdown content to a file.

**Parameters:**
- `md_content` (str): Markdown text to save
- `output_path` (str): Path to output file

### `save_structure_as_json()`

Exports document structure to JSON format.

**Parameters:**
- `document`: Docling document object
- `output_path` (str): Path to output JSON file

### `print_structure()`

Prints document structure hierarchy focusing on articles and sections.

**Parameters:**
- `document`: Docling document object

### `split_contract_by_article()`

Splits a markdown file by article sections and prints statistics.

**Parameters:**
- `file_path` (str): Path to markdown file

## Logging

The module uses Python's `logging` module. Enable logging to monitor conversion progress:

```python
import logging

logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
```

## Performance Notes

- **OCR disabled by default** to prevent character "guessing" on digital PDFs
- **Table structure enabled by default** for structured data preservation
- Conversion speed depends on document size and complexity
- Consider reusing `DocumentConverter` instance for batch processing multiple files

## Error Handling

The refactored function includes comprehensive error handling:

```python
try:
    doc = convert_to_markdown_by_docling("file.pdf")
except FileNotFoundError:
    print("Input file does not exist")
except RuntimeError as e:
    print(f"Conversion failed: {e}")
```

## Dependencies

- **docling**: Document conversion library
- **pathlib**: Modern path handling (Python stdlib)
- **logging**: Logging support (Python stdlib)
- **typing**: Type hints (Python stdlib)
- **re**: Regex for splitting (Python stdlib)
- **json**: JSON export (Python stdlib)

## Best Practices

1. **Use type hints**: The refactored function includes full type annotations
2. **Handle errors**: Always catch `FileNotFoundError` and `RuntimeError`
3. **Enable logging**: Configure logging for production use
4. **Reuse converters**: Pass a converter instance when processing multiple files
5. **Validate paths**: Use `pathlib.Path` for cross-platform compatibility

## License

This utility is provided as-is for document conversion tasks.

## See Also

- [Docling Documentation](https://github.com/DS4SD/docling)
- [Alternative Scripts](./): `pdf_to_md.py`, `pdf_to_md3.py`
