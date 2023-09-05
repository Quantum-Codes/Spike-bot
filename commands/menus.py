import discord, random
from main import guild_ids
from components.buttons import ConfirmWinners


class message_commands(discord.Cog):
  def __init__(self, bot):
    self.bot = bot

  @discord.message_command(name="giveaway", guild_ids= guild_ids)
  async def giveaway_winner(self, ctx, message):
    await ctx.defer(ephemeral=True)
    content = ""
    participants = []
    for item in message.reactions:
      #content += str(item.emoji)
      participants.extend([I.name for I in await item.users().flatten()])
      #content += "\n"
    participants = set(participants)
    content = f"The winners are:\n **@{',<ENTERCHR101>@'.join(random.sample(participants, 5))}**\n(First x winners are given the reward where x = number of rewards)\n\n **Participants**: {', '.join(participants)}".replace("<ENTERCHR101>", "\n") #can't use backslash in fitting expressions
    await ctx.followup.send(content, ephemeral = True, view=ConfirmWinners())

def setup(bot):
  bot.add_cog(message_commands(bot))