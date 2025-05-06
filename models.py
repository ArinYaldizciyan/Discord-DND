from peewee import *
from db import db

class BaseModel(Model):
    class Meta:
        database = db

class Player(BaseModel):
    discord_id = CharField(unique=True)

    class Meta:
        database = db

class Campaign(BaseModel):
    owner = ForeignKeyField(Player, backref='campaigns')
    server_id = CharField()
    campaign_name = CharField()
    campaign_theme = TextField()

class CampaignParticipant(BaseModel):
    player = ForeignKeyField(Player, backref='participations')
    campaign = ForeignKeyField(Campaign, backref='participants')

    class Meta:
        constraints = [SQL('UNIQUE(player_id, campaign_id)')]



class Character(BaseModel):
    player = ForeignKeyField(Player, backref='characters')
    campaign = ForeignKeyField(Campaign, backref='characters')
    character_hp = IntegerField()
    character_name = CharField()
    character_class = CharField()

class Inventory(BaseModel):
    character = ForeignKeyField(Character, backref='inventory')
    item_name = CharField()
    item_description = TextField()
    item_quantity = IntegerField()


    
    

