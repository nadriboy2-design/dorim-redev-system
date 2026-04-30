import pdfplumber
import sys

pdf_path = sys.argv[1]
with pdfplumber.open(pdf_path) as pdf:
    print(f'Total Pages: {len(pdf.pages)}')
    for i, page in enumerate(pdf.pages[:15]):
        text = page.extract_text()
        if text and len(text.strip()) > 10:
            print(f'--- Page {i+1} ---')
            print(text[:3000])
            print()
