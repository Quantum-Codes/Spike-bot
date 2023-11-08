import discord, random, string
from db import db, sql

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

class GiveawayJoin(discord.ui.View):
  def __init__(self):
    super().__init__(timeout=None) #persistent view

  @discord.ui.button(label= "Join Giveaway", style=discord.ButtonStyle.primary, emoji="🎁", custom_id = "meisid2")
  async def join_callback(self, button, interaction):
    await interaction.response.defer(ephemeral=True)
    if db.check_joined_giveaway(interaction.message.id, interaction.user.id):
      await interaction.followup.send("You have already joined the giveaway. <leave button>", ephemeral=True)
      return
    
    db.join_leave_giveaway(interaction.message.id, interaction.user.id, mode="join")
    await interaction.followup.send("Joined the giveaway!", ephemeral= True)
    