import discord

class ConfirmWinners(discord.ui.View):
  def __init__(self):
    super().__init__(timeout = 240)
    
  async def on_timeout(self):
    self.disable_all_items()
    await self.message.edit(":warning:You took longer than 4 minutes. Buttons disabled.:warning:\n"+self.message.content, view=self)
  
  @discord.ui.button(label= "Confirm", style=discord.ButtonStyle.primary, emoji=None)
  async def confirm_callback(self, button, interaction):
    self.disable_all_items()
    button.label = "Approved."
    button.style = discord.ButtonStyle.success
    await interaction.response.edit_message(view=self)
    await interaction.channel.send(interaction.message.content)
    
  @discord.ui.button(label= "Cancel", style=discord.ButtonStyle.danger, emoji=None)
  async def cancel_callback(self, button, interaction):
    self.disable_all_items()
    button.label = "Cancelled."
    button.style = discord.ButtonStyle.gray
    await interaction.response.edit_message(view=self)
    await interaction.followup.send("Trigger giveaway command again to choose new winners.", ephemeral = True)

 