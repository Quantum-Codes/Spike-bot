import discord, random, json
from main import guild_ids
from components.buttons import ConfirmWinners
from components.modals import GetWinnersCount
from db import db

""" USELESS. keeping for structure of message commands
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
    await ctx.defer(ephemeral=True)
    if ctx.author.id in [638738610564235265,718830331356250202]:
      if not db.check_valid_giveaway(message.id):
         await ctx.send("not valid giveaway")
         return 
      data = db.end_giveaway(message.id)
      content = f":tada:<:juuzou_gaming:1125994304528187392>**Giveaway Winner Announcement!**<:juuzou_gaming:1125994304528187392>:tada:\nThe winners are:\n**<@!{'> ,<ENTERCHR101><@!'.join([str(ab[0]) for ab in data['winners']])}>**\n\n:partying_face:Congratulations!!:partying_face:\n\n`Participants: {data['participants_count']}`".replace("<ENTERCHR101>", "\n")
      view = ConfirmWinners()
      message = await ctx.followup.send(content, ephemeral = True, view = view)
      view.message = message # to pass context
    else:
      await ctx.send("who to are you??", ephemeral = True)
  

def setup(bot):
  bot.add_cog(message_commands(bot))
"""