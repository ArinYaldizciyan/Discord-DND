from typing import Annotated, List, TypedDict

from langchain_ollama import OllamaLLM, ChatOllama
from langchain_core.messages import AIMessage, HumanMessage, SystemMessage
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.tools import tool
from langchain_core.prompts import ChatPromptTemplate
from langgraph.checkpoint.memory import MemorySaver
from langgraph.graph.message import add_messages, AnyMessage
from langgraph.graph import StateGraph, START, END, State
from langgraph.prebuilt import create_react_agent
from tools import roll_dice, get_user_input


#Create agent
memory = MemorySaver()
model = ChatOllama(model="llama3.2", temperature=0)
tools = [roll_dice, get_user_input]
agent_executor = create_react_agent(model, tools, checkpointer=memory)


class State(TypedDict):
    history: Annotated[List[AnyMessage], add_messages]
    player_information: Annotated