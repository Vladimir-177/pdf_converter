# pip install docling

from docling.document_converter import DocumentConverter, PdfFormatOption
from docling.datamodel.pipeline_options import PdfPipelineOptions
from docling_core.types.doc.labels import DocItemLabel

import warnings
from pathlib import Path
import logging
from typing import Optional, Any

import re
import json
import time



def convert_to_markdown_by_docling(
    input_file: str | Path,
    *,
    do_ocr: bool = False,
    do_table_structure: bool = True,
    converter: Optional[DocumentConverter] = None,
) -> Any:
    """Convert a PDF or DOCX to a Docling Document ready for export.

    Parameters
    - input_file: path to the input PDF or DOCX file
    - do_ocr: enable OCR (default False)
    - do_table_structure: attempt to preserve table structure (default True)
    - converter: optional `DocumentConverter` instance to reuse

    Returns the underlying document object (`result.document`). Raises
    `FileNotFoundError` if the input does not exist and `RuntimeError` on
    conversion errors.
    """
    logger = logging.getLogger(__name__)

    path = Path(input_file)
    if not path.exists():
        raise FileNotFoundError(f"Input file not found: {path}")

    # Configure PDF pipeline options
    pipeline_options = PdfPipelineOptions()
    pipeline_options.do_ocr = bool(do_ocr)
    pipeline_options.do_table_structure = bool(do_table_structure)

    # Create or augment a converter instance
    if converter is None:
        converter = DocumentConverter(
            format_options={"pdf": PdfFormatOption(pipeline_options=pipeline_options)} # type: ignore
        )
    else:
        try:
            if hasattr(converter, "format_options") and isinstance(converter.format_options, dict): # type: ignore
                converter.format_options.setdefault( # type: ignore
                    "pdf", PdfFormatOption(pipeline_options=pipeline_options)
                )
        except Exception:
            logger.debug("Unable to augment provided converter's format options", exc_info=True)

    # Run conversion with error handling
    try:
        result = converter.convert(str(path))
    except Exception as exc:  # keep broad to surface library errors clearly
        logger.exception("Conversion failed for %s", path)
        raise RuntimeError(f"Document conversion failed: {exc}") from exc

    return result.document






def save_markdown(md_content, output_path):
    with open(output_path, "w", encoding="utf-8") as f:
        f.write(md_content)

    # # 4. Export the entire document as structured Markdown
    # markdown_output = result.document.export_to_markdown()
    # with open(md_path, "w", encoding="utf-8") as f:
    #     f.write(markdown_output)

    # with open(json_path, "w") as f:
    #     json.dump(structure_dict, f, indent=2)

def convert_to_markdown(input_file_name, output_folder, file_type="pdf"):
    warnings.warn(
        "old_calculate_fees is deprecated and will be removed in v2.0. Use new_fee_calc instead.",
        category=DeprecationWarning,
        stacklevel=2
    )


    md_path = output_folder + input_file_name.split("/")[-1].replace(f".{file_type}", ".md")
    json_path = output_folder + input_file_name.split("/")[-1].replace(f".{file_type}", ".json")

    converter = DocumentConverter()
    result = converter.convert(input_file_name)
    structure_dict = result.document.export_to_dict()
    
    # Export the entire document as structured Markdown
    markdown_output = result.document.export_to_markdown()
    with open(md_path, "w", encoding="utf-8") as f:
        f.write(markdown_output)

    with open(json_path, "w") as f:
        json.dump(structure_dict, f, indent=2)

    return result.document


def save_structure_as_json(document, output_path):
    structure_dict = document.export_to_dict()
    with open(output_path, "w") as f:
        json.dump(structure_dict, f, indent=2)  


def print_structure(document):
    print("--- LIST OF ARTICLES / SECTIONS ---")
    # Iterate through all structural items
    for item, level in document.iterate_items():
        indent = "  " * level
        if (item.label in [DocItemLabel.TEXT, DocItemLabel.SECTION_HEADER, DocItemLabel.TITLE] 
            and item.text.lstrip("# ").startswith("ARTICLE")):
            print(f"{indent}[Level {level}] {item.text}")      
        



def split_by_article(file_path):
    with open(file_path, "r", encoding="utf-8") as f:
        content = f.read()

    # Regex breakdown:
    # (?=ARTICLE) is a 'lookahead' - it splits AT the word ARTICLE 
    # but keeps the word "ARTICLE" at the start of the next chunk.
    sections = re.split(r'(?=ARTICLE)', content)

    # Remove any empty first element if the file didn't start with "ARTICLE"
    sections = [s.strip() for s in sections if s.strip()]

    print(f"{'Section Name':<60} | {'Chars':<10} | {'Words':<10}")
    print("-" * 75)

    for i, section in enumerate(sections):
        # Extract first line to use as a title (e.g., "ARTICLE 1: DEFINITIONS")
        first_line = section.split('\n')[0][:60].strip()
        
        char_len = len(section)
        word_count = len(section.split())

        print(f"{first_line:<60} | {char_len:<10} | {word_count:<10}")




def split_contract_by_article(file_path):
    with open(file_path, "r", encoding="utf-8") as f:
        content = f.read()

    # Regex breakdown:
    # (?= ... )  -> Positive Lookahead (splits BEFORE the match, keeping it in the next chunk)
    # ^          -> Start of a line (requires re.MULTILINE flag)
    # [#\s]* -> Zero or more '#' or space characters
    # ARTICLE    -> The literal word
    # \b         -> Word boundary (prevents matching "ARTICLES" or "ARTICULATED")
    pattern = r'(?m)^(?=[#\s]*ARTICLE\b)'
    
    # Split the content
    sections = re.split(pattern, content, flags=re.IGNORECASE)

    # Clean up empty strings and whitespace
    sections = [s.strip() for s in sections if s.strip()]

    print(f"{'Section Header':<60} | {'Chars':<10} | {'Words':<10}")
    print("-" * 75)

    for section in sections:
        # Get the first line to identify the article
        header_line = section.split('\n')[0].strip()
        # Truncate header for display if too long
        display_header = (header_line[:57] + '..') if len(header_line) > 57 else header_line
        
        char_count = len(section)
        word_count = len(section.split())

        print(f"{display_header:<60} | {char_count:<10} | {word_count:<10}")



def main():
    input_file_name = "./data/sample A101-2017 (90 pages).pdf"
    # input_file_name = "./data/sample a101-2017_exhibit_A.pdf" 
    output_folder = "./data/output/"

    start_time = time.perf_counter()
    # 1. pdf -> markdown
    print("\n--- PDF to Markdown Conversion ---")
    res_doc = convert_to_markdown_by_docling(input_file_name)
    # res_doc = convert_to_markdown_docling_2(input_file_name, output_folder, file_type="pdf")

    # 2a. Save the markdown content to a file
    markdown_content = res_doc.export_to_markdown()
    md_output_path = output_folder + input_file_name.split("/")[-1].replace(".pdf", ".md")
    save_markdown(markdown_content, md_output_path)

    # 2b. Save the structure as JSON
    json_output_path = output_folder + input_file_name.split("/")[-1].replace(".pdf", ".json")
    save_structure_as_json(res_doc, json_output_path)   

    # 3. print structure of the document
    print_structure(res_doc)
    
    # 4. split markdown by article
    print("\n--- Article Splitting ---")
    file_name_md = output_folder + input_file_name.split("/")[-1].replace(".pdf", ".md")
    split_by_article(file_name_md)

    # 5. split markdown by article (using regex)
    print("\n--- Article Splitting with Regex ---")
    split_contract_by_article(file_name_md)
    end_time = time.perf_counter()

    
    duration = end_time - start_time
    print(f"--- Conversion Completed in {duration:.2f} seconds ---")
    


if __name__ == "__main__":
    main()