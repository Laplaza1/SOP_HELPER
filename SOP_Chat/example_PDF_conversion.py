# Language: Python
import pypdfium2 as pdfium

# Load PDF document

def extract_pdf(file:str):
    pdf = pdfium.PdfDocument(file)
    
    # Extract text from each page
    for i, page in enumerate(pdf):
        textpage = page.get_textpage()
        text = textpage.get_text_range()
        print(f"Page {i+1}:{text}")

    # Close the document
    pdf.close()