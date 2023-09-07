import discord, json, random
from components.buttons import ConfirmWinners

class GetWinnersCount(discord.ui.Modal):
  def __init__(self, *args, **kwargs):
    self.message = kwargs.pop("message") #or could do __init__(self, message, *args, **kwargs)
    super().__init__(*args, **kwargs)
    self.add_item(discord.ui.InputText(label="Number of winners: ", placeholder="Number of winners"))

  async def callback(self, interaction):
    winners = self.children[0].value
    if not winners.isdigit():
      await interaction.response.send_message("Value must be an integer", ephemeral = True)
      return

    await interaction.response.defer(ephemeral=True)
    winners = int(winners)
    content = ""
    participants = []
    with interaction.channel.typing():
      for item in self.message.reactions:
        #content += str(item.emoji)
        participants.extend([I.name for I in await item.users().flatten()])
        #content += "\n"
      participants = list(set(participants))
      content = f":tada:<:juuzou_gaming:1125994304528187392>**Giveaway Winner Announcement!**<:juuzou_gaming:1125994304528187392>:tada:\nThe winners are:\n**@{',<ENTERCHR101>@'.join(random.sample(participants, winners))}**\n\n:partying_face:Congratulations!!:partying_face:\n\nParticipants: ```{', '.join(participants)[:-2]}```".replace("<ENTERCHR101>", "\n")
    view = ConfirmWinners()
    message = await interaction.followup.send(content, ephemeral = True, view = view)
    view.message = message