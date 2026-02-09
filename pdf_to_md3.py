# pip install marker-pdf

import os
from marker.convert import convert_single_pdf
from marker.models import load_all_models


input_pdf = "./data/sample A101-2017 (90 pages).pdf"
# input_pdf = "./data/sample a101-2017_exhibit_A.pdf"
output_md = "./data/output_3.md"

# Note: Marker performs best on a GPU
model_lst = load_all_models()
full_text, images, out_meta = convert_single_pdf(input_pdf, model_lst)

with open(output_md, "w") as f:
    f.write(full_text)





# from marker.converters.pdf import PdfConverter
# from marker.models import create_model_dict
# from marker.output import text_from_rendered

# input_pdf = "./data/sample A101-2017 (90 pages).pdf"
# # input_pdf = "./data/sample a101-2017_exhibit_A.pdf"
# output_md = "./data/output_3.md"


# # 1. Initialize the new 2026 Converter
# # This automatically loads the necessary AI models
# converter = PdfConverter(
#     artifact_dict=create_model_dict(),
# )

# # 2. Run the conversion on your contract
# # This returns a 'rendered' object containing text, layout, and images
# rendered = converter(input_pdf)

# # 3. Extract the text (Markdown) and save it
# full_markdown, _, _ = text_from_rendered(rendered)

# with open(output_md, "w", encoding="utf-8") as f:
#     f.write(full_markdown)

# print("Conversion complete! Check output.md")


