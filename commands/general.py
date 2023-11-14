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
    msg = await ctx.send("`@everyone`",embed=discord.Embed(description = message), view=GiveawayJoin())
    db.create_giveaway(msg.id, winners)
    await ctx.followup.send("Success", ephemeral=True)
    

def setup(bot):
  bot.add_cog(generalcommands(bot))