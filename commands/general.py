import discord
from discord.commands import SlashCommandGroup
from main import guild_ids
from db import db
from components.buttons import GiveawayJoin, ConfirmWinners


class generalcommands(discord.Cog):
  def __init__(self, bot):
    self.bot = bot

  giveaway = SlashCommandGroup("giveaway", "Handle giveaways.", guild_ids=guild_ids)
  utility = SlashCommandGroup("utility", "Server enhancers", guild_ids=guild_ids)
    
  @discord.slash_command(name="servers", description ="list out servers I'm in", guild_ids=guild_ids)
  async def serverscommand(self, ctx):
    await ctx.send('\n'.join(guild.name for guild in self.bot.guilds))
    
  @giveaway.command(name="create", description = "Host a giveaway")
  async def giveaway_maker(self, ctx, message : str, winners : int):
    await ctx.defer(ephemeral=True)
    if ctx.author.id not in [638738610564235265,718830331356250202]:
      await ctx.followup.send("Who tf are you??", ephemeral = True)
      return

    msg = await ctx.send("`@everyone`",embed=discord.Embed(description = message), view=GiveawayJoin())
    db.create_giveaway(msg.id, winners)
    await ctx.followup.send("Success", ephemeral=True)

  @giveaway.command(name="end", description = "Ends a giveaway")
  async def giveaway_end(self, ctx, messageid: discord.Message, reward: str):
    await ctx.defer(ephemeral=True)
    message = messageid #alias
    if ctx.author.id not in [638738610564235265,718830331356250202]:
      await ctx.followup.send("Who tf are you??", ephemeral = True)
      return
    if not db.check_valid_giveaway(message.id):
      await ctx.followup.send("not valid giveaway", ephemeral=True)
      return 

    data = db.end_giveaway(message.id)
    title = f"The giveaway for **__{data['winners_count']}x {reward}__** has come to an end and"
    content = f"## 🎊<:juuzou_gaming:1125994304528187392>Giveaway Winner Announcement!<:juuzou_gaming:1125994304528187392>🎊\n{title} \n\n🥳The winners are:\n**<@!{'> ,<ENTERCHR101><@!'.join([str(ab[0]) for ab in data['winners']])}>**!!🥳\n\n:tada:Congratulations!!:tada:\n\n`Participants: {data['participants_count']}`".replace("<ENTERCHR101>", "\n")
    view = ConfirmWinners(message.id)
    message = await ctx.followup.send(embed=discord.Embed(colour= discord.Colour.green(), description=content), ephemeral = True, view = view)
    view.message = message # to pass context

  @giveaway.command(name="cleanup", description = "⚠️Deletes all data related to giveaway⚠️. Don't use this unless all rewards are claimed and no further rerolls are required.")
  async def giveaway_cleanup(self, ctx, messageid: discord.Message, confirm: bool):
    await ctx.defer(ephemeral=True)
    message = messageid #alias
    if ctx.author.id not in [638738610564235265,718830331356250202]:
      await ctx.followup.send("Who tf are you??", ephemeral = True)
      return
    if not db.check_valid_giveaway(message.id):
      await ctx.followup.send("not valid giveaway", ephemeral=True)
      return 
    if not confirm:
      await ctx.followup.send("Cancelled cleanup.", ephemeral=True)
      return

    db.cleanup_giveaway(message.id)
    await ctx.followup.send(f"Deleted all data related to the giveaway with **ID: {message.id}**")
  
  @utility.command(name="welcome", description="Set welcome message channel")
  async def welcomer(self, ctx, channel: discord.TextChannel, message: str):
    await ctx.send(channel.id)

def setup(bot):
  bot.add_cog(generalcommands(bot))