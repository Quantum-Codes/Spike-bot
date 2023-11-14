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
    if ctx.author.id in [638738610564235265,718830331356250202]:
      await ctx.send_modal(GetWinnersCount(title="Set Winners", message =message))
    else:
      await ctx.send("who tf are you??", ephemeral=True)
    #await ctx.followup.send()#, view=GetWinnersCount())

  @discord.message_command(name="EndGiveaway")
  async def giveaway_end(self, ctx, message):
    if ctx.author.id in [638738610564235265,718830331356250202]:
      pass
    else:
      await ctx.send("who to are you??", ephemeral = True)      
  

def setup(bot):
  bot.add_cog(message_commands(bot))