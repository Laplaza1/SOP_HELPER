# Language: Python
import pypdfium2 as pdfium
from .embeder import *
from .qdrant import *
import uuid
# Load PDF document

def extract_pdf(file:str,sop):
    pdf = pdfium.PdfDocument(file)
    print(pdf)
    
    

    
    # Extract text from each page
    for i, page in enumerate(pdf):
        textpage = page.get_textpage()
        text = textpage.get_text_range()
        embeding = fastembeder(text)
        id= str(uuid.uuid4())
        payload = {
                    "ServiceLevel":"User",
                    "sop":sop,
                    "step":text
                        }
        client.upsert(collection_name=QDRANT_COLLECTION,wait=True,points=[PointStruct(id =id,vector=embeding,payload=payload)])
        #print(f"Page {i+1}:{text}")

    # Close the document
    pdf.close()