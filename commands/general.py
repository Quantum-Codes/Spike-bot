import discord
from main import guild_ids
from db import db, sql
from components.buttons import GiveawayJoin
class generalcommands(discord.Cog):
  def __init__(self, bot):
    self.bot = bot

  @discord.slash_command(name="servers", description ="list out servers I'm in", guild_ids=guild_ids)
  async def serverscommand(self, ctx):
    await ctx.send('\n'.join(guild.name for guild in self.bot.guilds))

  @discord.slash_command(name="giveaway", description = "Host a giveaway", guild_ids = guild_ids)
  async def giveaway_maker(self, ctx, message : str, winners : int):
    await ctx.defer(ephemeral=True)
    """
    async def join_callback(self, button, interaction):
      await interaction.response.defer(ephemeral=True)
      if db.check_joined_giveaway(interaction.message.id, interaction.user.id):
        await interaction.followup.send("You have already joined the giveaway. <leave button>", ephemeral=True)
        return
      db.join_leave_giveaway(interaction.message.id, interaction.user.id, mode="join")
      await interaction.followup.send("Joined the giveaway!", ephemeral= True)
    
    msg = await ctx.send("hehe") #first get msg id
    view = discord.ui.View(timeout = None)
    button = discord.ui.Button(label="Join Giveaway", emoji="🎁", custom_id=f"gaw_{msg.id}")
    button.callback = join_callback
    view.add_item(button)
    """
    msg = await ctx.send("`@everyone`",embed=discord.Embed(description = message), view=GiveawayJoin())
    db.create_giveaway(msg.id, winners)
    await ctx.followup.send("Success", ephemeral=True)
    

def setup(bot):
  bot.add_cog(generalcommands(bot))