from qdrant_client import QdrantClient
from qdrant_client.http.models import Distance, VectorParams, PointStruct, Filter
from qdrant_client.models import PointStruct
import dotenv

import os
dotenv.load_dotenv(".env")

QDRANT_HOST = os.getenv("QDRANT_HOST")
QDRANT_API_KEY = None 
QDRANT_COLLECTION = "sop"  


client = QdrantClient(
    url=QDRANT_HOST,
    api_key=None
)


 
def get_or_create_collection():
    """
    Description:
        Creates collection using the qdrant_client module.
        Automatically makes a collection with a name specified in by the QDRANT_COLLECTION var.
        Default config is the size of the embedding vector which is 384 and they MUST match
        Distance is set to COSINE.

    
    
    """
    #Create Collection
    if not client.collection_exists(QDRANT_COLLECTION):
        client.create_collection(
            collection_name=QDRANT_COLLECTION,
            vectors_config=VectorParams(size=384, distance=Distance.COSINE),  # Match your embedder dim
        )
