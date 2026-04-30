import pdfplumber
import sys

pdf_path = sys.argv[1]
output_path = sys.argv[2]

with pdfplumber.open(pdf_path) as pdf:
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(f'Total Pages: {len(pdf.pages)}\n\n')
        for i, page in enumerate(pdf.pages):
            text = page.extract_text()
            if text and len(text.strip()) > 10:
                f.write(f'--- Page {i+1} ---\n')
                f.write(text[:5000])
                f.write('\n\n')

print('Done')
