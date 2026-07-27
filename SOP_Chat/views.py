from django.shortcuts import render
from django.http import HttpResponse, JsonResponse
from .qdrant import *
import numpy
from .embeder import *
from django.views.decorators.csrf import csrf_exempt
import uuid






def base(request):
    print("Base get collection",get_or_create_collection())

@csrf_exempt
def create_sop(request):
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


def semantic_search(request):
    """
    Checks query within sops
    """
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

    return render(request, 'base.html', {'results': hits ,'scores': hits})