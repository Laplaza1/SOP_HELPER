from qdrant_client import QdrantClient
from qdrant_client.http.models import Distance, VectorParams, PointStruct, Filter
from qdrant_client.models import PointStruct


import os


QDRANT_HOST = os.getenv("QDRANT_HOST", "http://localhost:32768")
QDRANT_API_KEY = None 
QDRANT_COLLECTION = "sop"  

client = QdrantClient(
    url=QDRANT_HOST,
    api_key=None
)


 
def get_or_create_collection():
    #Create Collection
    if not client.collection_exists(QDRANT_COLLECTION):
        client.create_collection(
            collection_name=QDRANT_COLLECTION,
            vectors_config=VectorParams(size=384, distance=Distance.COSINE),  # Match your embedder dim
        )
