# pip install markitdown[pdf]

from markitdown import MarkItDown

# input_pdf = "./data/sample a101-2017_exhibit_A.pdf"
input_pdf = "./data/sample A101-2017 (90 pages).pdf"
output_md = "./data/output.md"

md = MarkItDown(enable_plugins=False) # Set to True to enable plugins
result = md.convert(input_pdf)


# print(result.text_content)
try:
    with open(output_md, "w", encoding="utf-8") as f:
        f.write(result.text_content)
    print("Success! The contract has been saved to output.md")
except Exception as e:
    print(f"An error occurred while saving: {e}")