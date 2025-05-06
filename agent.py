from typing import Annotated, Dict, List, TypedDict

from langchain_ollama import OllamaLLM, ChatOllama
from langchain_core.messages import AIMessage, HumanMessage, SystemMessage, ToolMessage
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.tools import tool
from langchain_core.prompts import ChatPromptTemplate
from langgraph.checkpoint.memory import MemorySaver
from langgraph.graph.message import add_messages, AnyMessage
from langgraph.graph import StateGraph, START, END, State, build_graph
from langgraph.prebuilt import create_react_agent, ToolNode, tools_condition
from tools import roll_dice, get_user_input
from models import Player, Character, Campaign, Inventory
from playhouse.shortcuts import model_to_dict
from langgraph.checkpoint.memory import MemorySaver
#Create agent
llm = ChatOllama(model="llama3.2", temperature=0)
tools = [roll_dice, get_user_input]
llm_with_tools = llm.bind_tools(tools)

# Memory-backed state checkpointing (could swap with Redis later)
memory = MemorySaver()

# In-memory campaign runner registry
active_campaigns = {}


def build_campaign_state(server_id: str, campaign_id: str) -> dict:
    campaign = Campaign.get(Campaign.campaign_id == campaign_id)
    characters = [
        model_to_dict(c) for c in Character.select().where(Character.campaign == campaign)
    ]
    #make the characters dict include character information like their inventory
    for character in characters:
        character["inventory"] = [
            model_to_dict(i) for i in Inventory.select().where(Inventory.character == character["id"])
        ]

    system_prompt = f"""
    You are a Dungeons and Dragons 5th edition DM.
    You are given a theme for the campaign. Try and create a story that matches the theme. Map out the world and the characters.
    You will map the theme by using the default 5th edition rules, and just "skinning" them to fit the theme. Keep the theme as consistent as possible throughout the narrative. 
    You are given a list of characters and their inventory.
    You are also given a list of tools that can be used to interact with the world.
    You are given a list of history of the campaign.
    You are given a list of tools that can be used to interact with the world.

    Continue the story of the campaign from the last message in the history. Use the tools to get information and continue the story.
    Be as creative as possible, try and create engaging and interesting stories. Consider funny adventures, horror stories, characters with complex depth.
    As well as fun enemies, puzzles, and traps. 
    """

    return {
        "system_prompt": system_prompt,
        "campaign_theme": campaign.theme,
        "campaign_id": campaign_id,
        "server_id": server_id,
        "characters": characters,
        "history": []
    }

def get_or_create_runner(server_id: str, campaign_id: str):
    if campaign_id in active_campaigns:
        return active_campaigns[campaign_id]

    # Create new graph
    graph = build_graph()
    runner = graph.compile(checkpointer=memory)

    # Save runner
    active_campaigns[campaign_id] = runner
    return runner

def start_campaign(server_id: str, campaign_id: str):
    state = build_campaign_state(server_id, campaign_id)
    runner = get_or_create_runner(server_id, campaign_id)
    
    result = runner.invoke(state, config={"configurable": {"thread_id": campaign_id}})
    return result

def build_graph():
    sg = StateGraph(dict)

    tool_node = ToolNode(tools=tools)
    sg.add_node("tool_node", tool_node)
    sg.add_node("DM_node", DM_node)
    sg.add_edge("tool_node", "DM_node")
    sg.add_conditional_edges(
        'DM_node', tools_condition
    )

    sg.set_entry_point("DM_node")

    return sg


def DM_node(state):
    system_prompt = state["system_prompt"]
    recent_history = state["history"][-10:]
    messages = [
        SystemMessage(content=system_prompt),
        *recent_history,
    ]
    
    ai_response = llm_with_tools.invoke(messages)

    state["history"].append(ai_response.content)
    return state