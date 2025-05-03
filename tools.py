from langchain.tools import BaseTool, StructuredTool, tool
from pydantic import BaseModel, Field
import random


class RollDiceInput(BaseModel):
    num_dice: int = Field(description="The number of dice to roll.")
    num_sides: int = Field(description="The number of sides on each die.")


@tool(description="Roll a certain number of dice with a certain number of sides.")
def roll_dice(num_dice: int, num_sides: int) -> int:
    """Roll a certain number of dice with a certain number of sides."""
    return random.randint(num_dice, num_sides * num_dice)


class GetUserInputInput(BaseModel):
    question: str = Field(description="The question to ask the user.")

@tool(description="Get user input")
def get_user_input(question: str) -> str:
    """Get user input."""
    return input(question)






