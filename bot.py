from discord_typings import MessageCreateEvent
from interactions import Client, ComponentContext, Intents, InteractionContext, ModalContext, component_callback, listen, modal_callback, slash_command, SlashContext, Message
import os
import re
from discord.action_row import join_campaign_action_row
from discord.modals import create_campaign_modal, create_character_modal
from dotenv import load_dotenv
load_dotenv()

bot = Client(intents=Intents.DEFAULT)
lobbies = {}
class LobbyState:
    def __init__(self, lobby_id: str, channel_id: str, message_id: str, campaign_theme: str):
        self.lobby_id = lobby_id
        self.channel_id = channel_id
        self.message_id = message_id
        self.game_started = False
        self.campaign_theme = campaign_theme
        self.players = {} # user_id -> character dict
        

# intents are what events we want to receive from discord, `DEFAULT` is usually fine

@listen()  # this decorator tells snek that it needs to listen for the corresponding event, and run this coroutine
async def on_ready():
    print("Ready")
    print(f"This bot is owned by {bot.owner}")


        
@slash_command(name="start_campaign", description="Start a new DND campaign!")
async def start_campaign(ctx: SlashContext):
    lobby_id = f"{ctx.guild_id}-{ctx.id}"
    modal = create_campaign_modal()
    await ctx.send_modal(modal=modal)
    modal_ctx: ModalContext = await ctx.bot.wait_for_modal(modal)

    # Get the campaign theme from the modal
    campaign_theme = modal_ctx.responses["campaign_theme"]
    
    # Send a message to the channel with the campaign theme
    msg = await modal_ctx.send(f"A new campaign has begun! The theme is: {campaign_theme}", components=join_campaign_action_row(f"join_{lobby_id}"))

    lobbies[lobby_id] = LobbyState(lobby_id, ctx.channel_id, msg.id, campaign_theme)

@component_callback(re.compile(r"^join_.*$"))
async def handle_join_campaign(ctx: ComponentContext):
    lobby_id = ctx.custom_id.split("_")[1]
    lobby = lobbies[lobby_id]
    if not lobby:
        return await ctx.send("Lobby not found", ephemeral=True)
    
    user_id = str(ctx.user.id)
    if user_id in lobby.players:
        return await ctx.send("You're already in this campaign", ephemeral=True)
    

    character_modal = create_character_modal(f"create_modal_{lobby_id}_{user_id}")
    await ctx.send_modal(modal=character_modal)

@modal_callback("create_modal_*_*")
async def on_character_created(ctx: ModalContext, character_name: str, character_class: str):
    modal_data = ctx.data
    _, lobby_id, user_id = modal_data.custom_id.split("_")

    components = modal_data.components
    await ctx.send(f"Character created: {character_name} the {character_class}", ephemeral=True)
bot.start(os.environ.get("DISCORD_BOT_KEY"))