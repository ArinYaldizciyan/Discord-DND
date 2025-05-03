from typing import List
from interactions import Modal, ShortText

def create_campaign_modal() -> Modal:
  modal = Modal (
    ShortText(label="Campaign Theme! Be creative!", custom_id="campaign_theme", required=True, min_length=3),
    title="Create a Campaign"
  )
  return modal

def create_character_modal(custom_id: str) -> Modal:
  modal = Modal(
    ShortText(label="Character's Name", required=True, min_length=3, placeholder="Argoth the Brave"),
    ShortText(label="Character's Class", required=True, min_length=3, placeholder="Paladin"),
    title="Create a Character",
    custom_id=custom_id
  )
  return modal


