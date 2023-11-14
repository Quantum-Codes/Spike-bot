import discord
from discord.commands import SlashCommandGroup
from main import guild_ids
from db import db
from components.buttons import GiveawayJoin, ConfirmWinners
class generalcommands(discord.Cog):
  def __init__(self, bot):
    self.bot = bot

  giveaway = SlashCommandGroup("giveaway", "Handle giveaways.", guild_ids=guild_ids)
    
  @discord.slash_command(name="servers", description ="list out servers I'm in", guild_ids=guild_ids)
  async def serverscommand(self, ctx):
    await ctx.send('\n'.join(guild.name for guild in self.bot.guilds))
  @giveaway.command(name="create", description = "Host a giveaway")
  async def giveaway_maker(self, ctx, message : str, winners : int):
    await ctx.defer(ephemeral=True)
    msg = await ctx.send("`@everyone`",embed=discord.Embed(description = message), view=GiveawayJoin())
    db.create_giveaway(msg.id, winners)
    await ctx.followup.send("Success", ephemeral=True)

  @giveaway.command(name="end", description = "Ends a giveaway")
  async def giveaway_end(self, ctx, messageid: discord.Message, reward: str):
    await ctx.defer(ephemeral=True)
    message = messageid #alias
    if ctx.author.id in [638738610564235265,718830331356250202]:
      if not db.check_valid_giveaway(message.id):
         await ctx.send("not valid giveaway")
         return 
      data = db.end_giveaway(message.id)
      title = f"The giveaway for **__{data['winners_count']}x {reward}__** has come to an end and"
      content = f"## 🎊<:juuzou_gaming:1125994304528187392>Giveaway Winner Announcement!<:juuzou_gaming:1125994304528187392>🎊\n{title} \n\n🥳The winners are:\n**<@!{'> ,<ENTERCHR101><@!'.join([str(ab[0]) for ab in data['winners']])}>**!!🥳\n\n:tada:Congratulations!!:tada:\n\n`Participants: {data['participants_count']}`".replace("<ENTERCHR101>", "\n")
      view = ConfirmWinners()
      message = await ctx.followup.send(embed=discord.Embed(colour= discord.Colour.green(), description=content), ephemeral = True, view = view)
      view.message = message # to pass context
    else:
      await ctx.send("who to are you??", ephemeral = True)

def setup(bot):
  bot.add_cog(generalcommands(bot))