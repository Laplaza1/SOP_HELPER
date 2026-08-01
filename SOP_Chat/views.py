from django.shortcuts import render
from django.http import HttpResponse, JsonResponse,HttpRequest
from .qdrant import *
import numpy
from .embeder import *
from django.views.decorators.csrf import csrf_exempt
import uuid
import openai
import os
import json
from openai import OpenAI
import logging
logging.basicConfig(filename='app.log', level=logging.INFO, datefmt='%y%m%d %H:%M:%S', format='%(levelname)s: %(message)s')
logger = logging.getLogger(__name__)


def chat_model(Query:str|None,Context:list[str]|None)->str|None:
    """
    
    Args:
        Query :(str|None): The query string.
        Context :(list[str]|None): The result of the the semanitic search


    Returns:
        (str|None): the output of the model
        
    
    """
    client = OpenAI(
        api_key=os.getenv("XAI_API_KEY"),
        base_url="https://api.x.ai/v1",
    )
    

    system_prompt = """
            You are a helpful assistant that elaborates on RAG search results.
            Use only the provided context to answer.
            Write clear, well-structured, and natural responses.
            Do not invent information.
            """

    user_prompt = f"""
            Question: {Query}

            Context:
            {Context}

            Please provide a detailed and helpful elaboration based on the context above.
            """

    response = client.chat.completions.create(
        model="grok-4.3",
        messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}
                 ],
        temperature=0.8,
        max_tokens=1024,
    )
   
    return response.choices[0].message.content



def base(request:HttpRequest):
    logger.info(f"route {base.__name__} started by {request.META.get("REMOTE_ADDR")}")
    print("Base get collection")
    return render(request,"base.html")

@csrf_exempt
def create_sop(request:HttpRequest)->JsonResponse:
    logger.info(f"route {create_sop.__name__} started by {request.META.get("REMOTE_ADDR")}")
    """
    Upserts an SOP with the struct 
    \n
    {'servicelevel': 'value',
    'sop':'value',
    'step': 'value'
    }
    """
    if request.method == "POST":
    
        items   = dict(request.POST)
        ServiceLevel =  items.get("serviceLevel", "")
        SOP =   items.get("sop", "")
        step =  items.get("step", "")
        
        if not SOP or not ServiceLevel or not step:
            logger.info(f"{request.META.get("REMOTE_ADDR")} forgot to include SOP or STEP")
            return JsonResponse({"error": "items are required."}, status=400)
        embeding = fastembeder(step)
        payload = {
            "ServiceLevel":ServiceLevel,
            "sop":SOP,
            "step":step
                   }

        id= str(uuid.uuid4())
        client.upsert(collection_name=QDRANT_COLLECTION,wait=True,points=[PointStruct(id = id,vector=embeding,payload=payload)])
        print("sop created")
        return JsonResponse({"message": f"Received {ServiceLevel} with SOP: {SOP} with embedding {embeding}"})


def semantic_search(request:HttpRequest)->HttpResponse:
    """
    Checks query within sops
    """

    logger.info(f"route {semantic_search.__name__} started by {request.META.get("REMOTE_ADDR")}")
    query = request.GET.get('q')
    sop = request.GET.get('sop')  
    if not query:
        return render(request, 'base.html', {'results': []})
    
    embeddings = fastembeder(query)
    hits = client.query_points(
        collection_name=QDRANT_COLLECTION,
        query=embeddings,
        limit=10,
        query_filter=Filter(must=[
            {
                "key":"sop",
                "match":{
                    "value": sop
                }
            }]), 
    )

    
    print(f"Found some hits for '{query}'")
    print(f"\nHits: {hits}")
    response = chat_model(Query=query,Context=hits)

    return render(request, 'base.html', {'results': response}) 