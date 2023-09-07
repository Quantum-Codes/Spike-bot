import discord 

class GetWinnersCount(discord.ui.Modal):
  def __init__(self, *args, **kwargs):
    super().__init__(*args, **kwargs)
    self.add_item(discord.ui.InputText(label="Number of winners: ", placeholder="Number of winners"))

  async def callback(self, interaction):
    await interaction.followup.send(type(self.children[0]))