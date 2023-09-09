import discord, random, json
from main import guild_ids
from components.modals import GetWinnersCount


class message_commands(discord.Cog):
  def __init__(self, bot):
    self.bot = bot

  @discord.message_command(name="giveaway")
  async def giveaway_winner(self, ctx, message):
    #await ctx.defer()
    #await ctx.defer(ephemeral=True)
    """
    print("works")
    
    """
    await ctx.send_modal(GetWinnersCount(title="Set Winners", message =message))
    #await ctx.followup.send()#, view=GetWinnersCount())

def setup(bot):
  bot.add_cog(message_commands(bot))