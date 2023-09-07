import discord, json

class GetWinnersCount(discord.ui.Modal):
  def __init__(self, *args, **kwargs):
    self.message = kwargs.pop("message") #or could do __init__(self, message, *args, **kwargs)
    super().__init__(*args, **kwargs)
    self.add_item(discord.ui.InputText(label="Number of winners: ", placeholder="Number of winners"))

  async def callback(self, interaction):
    winners = self.children[0].value()
    if not winners.isdigit():
      await interaction.response.send_message("Value must be an integer", ephemeral = True)
      return

    winners = int(winners)
    content = ""
    participants = []
    for item in self.message.reactions:
      #content += str(item.emoji)
      participants.extend([I.name for I in await item.users().flatten()])
      #content += "\n"
    participants = list(set(participants))
    await interaction.response.send_message(f"Participants: ```{json.dumps(participants)}```", ephemeral = True)