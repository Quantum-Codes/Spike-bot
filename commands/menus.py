import discord, random, json
from main import guild_ids
from components.buttons import ConfirmWinners
from components.modals import GetWinnersCount


class message_commands(discord.Cog):
  def __init__(self, bot):
    self.bot = bot

  @discord.message_command(name="giveaway", guild_ids= guild_ids)
  async def giveaway_winner(self, ctx, message):
    await ctx.send_modal(GetWinnersCount(title="Set Winners"))
    #await ctx.defer(ephemeral=True)
    print("works")
    content = ""
    participants = []
    for item in message.reactions:
      #content += str(item.emoji)
      participants.extend([I.name for I in await item.users().flatten()])
      #content += "\n"
    participants = list(set(participants))

    await ctx.followup.send(f"Participants: ```{json.dumps(participants)}```", ephemeral = True)#, view=GetWinnersCount())

def setup(bot):
  bot.add_cog(message_commands(bot))