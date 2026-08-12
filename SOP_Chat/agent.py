import openai
import scipy
import os
from typing import Annotated
from langchain_core.tools import tool, InjectedToolCallId
from langgraph.prebuilt import InjectedState
from langgraph.graph import StateGraph, START, MessagesState
from langgraph.types import Command

from langchain.agents import create_agent



def supervisor(Query:str|None,Context:list[str]|None):
    """
        
        Args:
            Query :(str|None): The query string.
            Context :(list[str]|None): The result of the the semanitic search
    
    
        Returns:
            (str|None): the output of the model
            
        
        """
    client = openai.OpenAI(
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
       
        #return response.choices[0].message.content
    
    pass

def chat_model(Query:str|None,Context:list[str]|None)->str|None:
    """
    
    Args:
        Query :(str|None): The query string.
        Context :(list[str]|None): The result of the the semanitic search


    Returns:
        (str|None): the output of the model
        
    
    """
    client = openai.OpenAI(
        api_key=os.getenv("XAI_API_KEY"),
        base_url="https://api.x.ai/v1",
    )
    

    system_prompt = """
            You are a helpful assistant that elaborates on RAG search results.
            Use only the provided context to answer.
            Write clear, well-structured, and natural responses.
            Do not invent information.
            If the SOP seems incorrect or indicated don't say anything to indicate that.
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



