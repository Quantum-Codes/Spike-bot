import discord
from discord.commands import SlashCommandGroup
from main import guild_ids
from db import db, funcs
from components.buttons import GiveawayJoin, ConfirmWinners


class giveawaycommands(discord.Cog):
  def __init__(self, bot):
    self.bot = bot

  giveaway = SlashCommandGroup("giveaway", "Handle giveaways.", guild_ids=guild_ids)

  async def cog_command_error(self, ctx, error):
    print(error, error.__cause__, type(error))
    if isinstance(error, discord.ext.commands.MessageNotFound):
      await ctx.respond('Message not found. Check the message ID and try again.', ephemeral = True)
    else:
      raise error

  @giveaway.command(name="create", description = "Host a giveaway")
  async def giveaway_maker(self, ctx, message : str, winners : int):
    await ctx.defer(ephemeral=True)
    if ctx.author.id not in [638738610564235265,718830331356250202]:
      await ctx.followup.send("Who tf are you??", ephemeral = True)
      return

    msg = await ctx.send(embed=discord.Embed(description = message), view=GiveawayJoin())
    db.create_giveaway(msg.id, ctx.channel.id, winners)
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
    title = f"The giveaway for **__{reward}__** for {data['winners_count']} winners has come to an end and"
    content = f"## 🎊<:juuzou_gaming:1125994304528187392>Giveaway Winner Announcement!<:juuzou_gaming:1125994304528187392>🎊\n{title} \n\n🥳The winners are:\n**<@!{'> ,<ENTERCHR101><@!'.join([str(ab['user_id']) for ab in data['winners']])}>**!!🥳\n\n:tada:Congratulations!!:tada:\n\n`Participants: {data['participants_count']}`".replace("<ENTERCHR101>", "\n")
    view = ConfirmWinners(message)
    message = await ctx.followup.send(embed=discord.Embed(colour= discord.Colour.green(), description=content), ephemeral = True, view = view)
    view.message = message # to pass context

  @giveaway.command(name="cleanup", description = "⚠️Deletes all data related to giveaway⚠️ Don't use unless no further rerolls required")
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

    await db.cleanup_giveaway(ctx, message.id)
    await ctx.followup.send(f"Deleted all data related to the giveaway with **ID: {message.id}**")
  

class utilitycommands(discord.Cog):
  def __init__(self, bot):
    self.bot = bot

  utility = SlashCommandGroup("utility", "Server enhancers", guild_ids=guild_ids)

  async def cog_command_error(self, ctx, error):
    print(error, error.__cause__, type(error))
    if isinstance(error, discord.ext.commands.MessageNotFound):
      await ctx.respond('Message not found. Check the message ID and try again.', ephemeral = True)
    else:
      raise error

  @discord.slash_command(name="servers", description ="list out servers I'm in", guild_ids=guild_ids)
  async def serverscommand(self, ctx):
    await ctx.send('\n'.join(guild.name for guild in self.bot.guilds))

  @utility.command(name="welcome", description="Set welcome message channel")
  async def welcomer(self, ctx, channel: discord.TextChannel, message: str, embed_title: str = "", ping_member: bool = True):
    embed = discord.Embed(colour = discord.Colour.green(), title="Saved welcome message", description = message)
    embed.add_field(name="channel", value=f"<#{channel.id}>")
    embed.add_field(name="title", value=embed_title)
    embed.add_field(name="ping new member", value = ping_member)
    embed.set_footer(text="Use `/utility welcometest` to preview the message")
    db.save_server_settings(ctx.guild.id, "welcomer", {"message": message, "channel": channel.id, "title": embed_title, "ping": ping_member})
    await ctx.respond(embed=embed)

  @utility.command(name="welcometest", description ="Test the welcome message")
  async def welcometest(self, ctx):
    data = db.get_server_settings(ctx.guild.id, "welcomer")
    if data is None:
      embed = discord.Embed(colour = discord.Colour.red(), description="No welcome message set for this server.\nSet it up using `/utility welcome` command.")
      await ctx.respond(embed = embed)
      return
    embed = discord.Embed(colour = discord.Colour.green(), title=funcs.replace_placeholders (data["title"], ctx, test=True), description =funcs.replace_placeholders(data["message"], ctx, test= True))
    embed.add_field(name="would have been posted in:", value=f"<#{data['channel']}>")
    await ctx.respond('@testuser' if data['ping'] else None, embed=embed)


def setup(bot):
  bot.add_cog(giveawaycommands(bot))
  bot.add_cog(utilitycommands(bot))