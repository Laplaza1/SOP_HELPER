

from sentence_transformers import SentenceTransformer
from fastembed import TextEmbedding
import time

def sentenceTransformer(input:str|int)->list:
    start = time.time()
    model = SentenceTransformer('all-MiniLM-L6-v2')
    embeddings = model.encode([input])

    print("Sentence Transformer took: ",time.time()-start)

    return embeddings



def fastembeder(input:str|int)->list:
    """

    Params 
        :input: Can be a string or an Int,this will be converted into an 384 dim array along with other numpy array information
    
    :Returns: List of 384 values
    
    """

    start = time.time()
    embedder = TextEmbedding()

    # Generate embeddings
    texts = input
    print(texts)
    embeddings = list(embedder.embed(texts))
    print(embeddings)
    print("fastembed took:",time.time()-start)


    return embeddings[0]



