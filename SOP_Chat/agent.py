import openai
import scipy
import os
from typing import Annotated
from langchain_core.tools import tool, InjectedToolCallId
from langgraph.prebuilt import InjectedState
from langgraph.graph import StateGraph, START, MessagesState
from langgraph.types import Command
from langgraph.types import Send
from langchain_core.messages import convert_to_messages
from langchain.agents import create_agent
import dotenv
import getpass

dotenv.load_dotenv(".env")

def _set_if_undefined(var: str):
    if not os.environ.get(var):
        os.environ[var] = getpass.getpass(f"Please provide your {var}")


_set_if_undefined("OPENAI_API_KEY")

client = openai.OpenAI(
            api_key=os.getenv("XAI_API_KEY"),
            base_url="https://api.x.ai/v1",
        )


def create_handoff_tool(*, agent_name: str, description: str | None = None):
    name = f"transfer_to_{agent_name}"
    description = description or f"Ask {agent_name} for help."

    @tool(name, description=description)
    def handoff_tool(
        state: Annotated[MessagesState, InjectedState],
        tool_call_id: Annotated[str, InjectedToolCallId],
    ) -> Command:
        tool_message = {
            "role": "tool",
            "content": f"Successfully transferred to {agent_name}",
            "name": name,
            "tool_call_id": tool_call_id,
        }
        # highlight-next-line
        return Command(
            # highlight-next-line
            goto=agent_name,  # (1)!
            # highlight-next-line
            update={**state, "messages": state["messages"] + [tool_message]},  # (2)!
            # highlight-next-line
            graph=Command.PARENT,  # (3)!
        )

    return handoff_tool

def pretty_print_message(message, indent=False):
    pretty_message = message.pretty_repr(html=True)
    if not indent:
        print(pretty_message)
        return

    indented = "\n".join("\t" + c for c in pretty_message.split("\n"))
    print(indented)


def pretty_print_messages(update, last_message=False):
    is_subgraph = False
    if isinstance(update, tuple):
        ns, update = update
        # skip parent graph updates in the printouts
        if len(ns) == 0:
            return

        graph_id = ns[-1].split(":")[0]
        print(f"Update from subgraph {graph_id}:")
        print("\n")
        is_subgraph = True

    for node_name, node_update in update.items():
        update_label = f"Update from node {node_name}:"
        if is_subgraph:
            update_label = "\t" + update_label

        print(update_label)
        print("\n")

        messages = convert_to_messages(node_update["messages"])
        if last_message:
            messages = messages[-1:]

        for m in messages:
            pretty_print_message(m, indent=is_subgraph)
        print("\n")


def create_task_description_handoff_tool(
    *, agent_name: str, description: str | None = None
):
    name = f"transfer_to_{agent_name}"
    description = description or f"Ask {agent_name} for help."

    @tool(name, description=description)
    def handoff_tool(
        # this is populated by the supervisor LLM
        task_description: Annotated[
            str,
            "Description of what the next agent should do, including all of the relevant context.",
        ],
        # these parameters are ignored by the LLM
        state: Annotated[MessagesState, InjectedState],
    ) -> Command:
        task_description_message = {"role": "user", "content": task_description}
        agent_input = {**state, "messages": [task_description_message]}
        return Command(
            # highlight-next-line
            goto=[Send(agent_name, agent_input)],
            graph=Command.PARENT,
        )

    return handoff_tool


def handle_SOP(file:str):
    split_agent = create_agent(
        model="openai:gpt-4.1",
        tools=[],
        system_prompt=(
            "You are a text-splitting agent.\n\n"
            "INSTRUCTIONS:\n"
            "- Assist ONLY with text splitting and segmentations tasks\n"
            "- After you're done with your tasks, respond to the supervisor directly\n"
            "- You are to split the text into coherent numbered sections if they aren't already.\n"
            "- Respond ONLY with the results of your work, do NOT include ANY other text."
        ),
        name="split_agent",)


    summerization_agent = create_agent(
        model="openai:gpt-4.1",
        tools=[],
        system_prompt=(
            "You are a summing agent.\n\n"
            "INSTRUCTIONS:\n"
            "- Assist ONLY with summing tasks\n"
            "- After you're done with your tasks, respond to the supervisor directly\n"
            "- You are to summarize the text into a coherent text.\n"
            "- Respond ONLY with the results of your work, do NOT include ANY other text."
        ),
        name="sum_agent",)

    logic_agent = create_agent(
        model="openai:gpt-4.1",
        tools=[],
        system_prompt=(
            "You are a logic agent.\n\n"
            "INSTRUCTIONS:\n"
            "- Assist ONLY with logic checking tasks\n"
            "- After you're done with your tasks, respond to the supervisor directly\n"
            "- You are to check the logic of a given text if valid do nothing else fix it.\n"
            "- Respond ONLY with the results of your work, do NOT include ANY other text."
        ),
        name="logic_agent",)

    assign_to_split_agent_with_description = create_task_description_handoff_tool(
    agent_name="split_agent",
    description="Assign task to a split agent.",
)

    assign_to_sum_agent_with_description = create_task_description_handoff_tool(
        agent_name="sum_agent",
        description="Assign task to a sum agent.",
    )

    assign_to_logic_agent_with_description = create_task_description_handoff_tool(
        agent_name="logic_agent",
        description="Assign task to a logic agent.",
    )

    supervisor_agent_with_description = create_agent(
        model="openai:gpt-4.1",
        tools=[
            assign_to_split_agent_with_description,
            assign_to_sum_agent_with_description,
            assign_to_logic_agent_with_description,
        ],
        system_prompt=(
            "You are a supervisor managing three agents:\n"
            "- a split agent. Assign text splitting tasks to this assistant\n"
            "- a summarization agent. Assign summarization related tasks to this assistant\n"
            "- a logic agent. Assign logic checking related tasks to this assistant\n"
            "Assign work to one agent at a time, do not call agents in parallel.\n"
            "Do not do any work yourself."
        ),
        name="supervisor",
    )

    supervisor_with_description = (
        StateGraph(MessagesState)
        .add_node(
            supervisor_agent_with_description, destinations=("split_agent", "sum_agent","logic_agent")
        )
        .add_node(split_agent)
        .add_node(summerization_agent)
        .add_node(logic_agent)
        .add_edge(START, "supervisor")
        .add_edge("split_agent", "supervisor")
        .add_edge("sum_agent", "supervisor")
        .add_edge("logic_agent", "supervisor")
        .compile()
    )


    for chunk in supervisor_with_description.stream(
        {
            "messages": [
                {
                    "role": "user",
                    "content": f"Make the following text into a usable SOP.\n{file}",
                }
            ]
        },
        subgraphs=True,
        
    ):
        open('agent.txt',"+a").write("\n"+str(chunk[1]))
        pretty_print_messages(chunk, last_message=True)





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


