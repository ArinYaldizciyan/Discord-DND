from discord_typings import MessageCreateEvent
from interactions import ActionRow, Button, ButtonStyle, Client, ComponentContext, Intents, InteractionContext, ModalContext, component_callback, listen, modal_callback, slash_command, SlashContext, Message
import os
import re
from discord.action_row import join_campaign_action_row
from discord.modals import create_campaign_modal, create_character_modal
from dotenv import load_dotenv
from collections import defaultdict
from models import Player, Campaign, Character, Inventory
from db import db
load_dotenv()

bot = Client(intents=Intents.DEFAULT, token=os.environ.get("DISCORD_BOT_KEY"))
lobbies = {}
user_campaigns = defaultdict(list)

def initialize_db():
    db.connect()
    db.create_tables([Player, Campaign, Character, Inventory], safe=True)

class LobbyState:
    def __init__(self, lobby_owner: str, lobby_id: str, campaign_name: str, channel_id: str, message_id: str, campaign_theme: str):
        self.lobby_owner = lobby_owner
        self.campaign_name = campaign_name
        self.lobby_id = lobby_id
        self.channel_id = channel_id
        self.message_id = message_id
        self.game_started = False
        self.campaign_theme = campaign_theme
        self.players = {} # user_id -> character dict

class LobbyCharacter:
    def __init__(self, character_name: str, class_name: str):
        self.name = character_name
        self.class_name = class_name

@listen()  # this decorator tells snek that it needs to listen for the corresponding event, and run this coroutine
async def on_ready():
    print("Ready")
    print(f"This bot is owned by {bot.owner}")
    print("initializing db...")
    initialize_db()

        
@slash_command(name="setup_campaign", description="Setup a new DND campaign!")
async def setup_campaign(ctx: SlashContext):
    lobby_id = f"{ctx.guild_id}-{ctx.id}"
    user_id = str(ctx.user.id)
    modal = create_campaign_modal()
    await ctx.send_modal(modal=modal)
    modal_ctx: ModalContext = await ctx.bot.wait_for_modal(modal)

    #Create a player if they don't exist
    owner, created = Player.get_or_create(discord_id=user_id)

    #Get the campaign name from the modal
    campaign_name = modal_ctx.responses["campaign_name"]
    # Get the campaign theme from the modal
    campaign_theme = modal_ctx.responses["campaign_theme"]
    
    # Send a message to the channel with the campaign theme
    msg = await modal_ctx.send(f"A new campaign has begun! The theme is: {campaign_theme}", components=join_campaign_action_row(f"join_{lobby_id}"))

    campaign = Campaign.create(owner=owner, server_id=str(ctx.guild_id), campaign_name=campaign_name, campaign_theme=campaign_theme)
    lobbies[lobby_id] = LobbyState(str(ctx.user.id), lobby_id, campaign_name, ctx.channel_id, msg.id, campaign_theme)
    user_campaigns[user_id].append(lobby_id)

@component_callback(re.compile(r"^join_.*$"))
async def handle_join_campaign(ctx: ComponentContext):
    lobby_id = ctx.custom_id.split("_")[1]
    lobby = lobbies.get(lobby_id)
    if not lobby:
        return await ctx.send("Lobby not found", ephemeral=True)
    
    user_id = str(ctx.user.id)
    if user_id in lobby.players:
        return await ctx.send("You're already in this campaign", ephemeral=True)
    
    character_modal = create_character_modal(f"create_modal_{lobby_id}_{user_id}")
    await ctx.send_modal(modal=character_modal)

@modal_callback(re.compile(r"^create_modal_[^_]+_[^_]+$"))
async def on_character_created(ctx: ModalContext, character_name: str, character_class: str):
    custom_id = ctx.custom_id
    lobby_id, user_id = custom_id.split("_")[2:]
    lobby = lobbies.get(lobby_id)
    #Create a player if they don't exist
    player, created= Player.get_or_create(discord_id=user_id)

    #Create a character
    character = Character.create(player=player, campaign=lobby.campaign, character_name=character_name, character_class=character_class)

    lobby.players[user_id] = LobbyCharacter(character_name, character_class)
    await ctx.send(f"Character created: {character_name} the {character_class}", ephemeral=True)

@slash_command(name="start_campaign", description="Start the campaign!")
async def start_campaign(ctx: SlashContext):
    user_id = str(ctx.user.id)
    campaigns = user_campaigns.get(user_id)

    if not campaigns:
        return await ctx.send("You have no campaigns to begin.", ephemeral=True)

    buttons = [
        Button(
            style=ButtonStyle.PRIMARY,
            label=lobbies[l_id].campaign_name,
            custom_id=f"begin_{l_id}"
        )
        for l_id in campaigns
    ]

    row = ActionRow(*buttons)
    await ctx.send("Choose a campaign to begin:", components=[row], ephemeral=True)

@component_callback(re.compile(r"^begin_.*$"))
async def begin_campaign(ctx: ComponentContext):
    custom_id = ctx.custom_id
    lobby_id = custom_id.split("_")[1]
    lobby = lobbies.get(lobby_id)
    print(lobby)
    await ctx.send(f"Campaign {lobby.campaign_name} started!", ephemeral=True)
    



bot.start()