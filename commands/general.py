import discord
from main import guild_ids 

class generalcommands(discord.Cog):
  def __init__(self, bot):
    self.bot = bot

  @discord.slash_command(name="servers", description ="list out servers I'm in", guild_ids=guild_ids)
  async def serverscommand(self, ctx):
    await ctx.send('\n'.join(guild.name for guild in self.bot.guilds))


def setup(bot):
  bot.add_cog(generalcommands(bot))