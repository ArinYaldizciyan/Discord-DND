import interactions
from typing import List
from interactions import EmbedFooter, ActionRow, Button, ButtonStyle, PartialEmoji


def join_campaign_action_row(custom_id: str) -> ActionRow:
  join_emoji = PartialEmoji.from_str("🧙🏻‍♂️")
  join_button = Button(label="Join Campaign", custom_id=custom_id,style=ButtonStyle.SUCCESS, emoji=join_emoji)
  action_row = ActionRow(join_button)
  return action_row
