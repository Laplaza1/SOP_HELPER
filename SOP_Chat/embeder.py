

from sentence_transformers import SentenceTransformer
from fastembed import TextEmbedding
import time

def sentenceTransformer(input:str|int)->list:
    """
    Desc:
        Uses all-MiniLM-L6-v2 to convert into 384 Dim Vectors
    
    """
    start = time.time()
    model = SentenceTransformer('all-MiniLM-L6-v2')
    embeddings = model.encode([input])

    print("Sentence Transformer took: ",time.time()-start)

    return embeddings



def fastembeder(input:str|int)->list:
    """
    Desc:
        creates embedding from BAAI/bge-small-en-v1.5 into a 384 Dim vector

    Params 
        :input: Can be a string or an Int,this will be converted into an 384 dim array along with other numpy array information
    
    :Returns: List of 384 values
    
    """

    start = time.time()
    embedder = TextEmbedding()

    # Generate embeddings
    texts = input
    embeddings = list(embedder.embed(texts))
    print("fastembed took:",time.time()-start)


    return embeddings[0]



