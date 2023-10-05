import discord, random
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
        participants.extend([I.name for I in await item.users().flatten()])
      participants = tuple(set(participants))
      participants_formatted = ', '.join(participants) #2000 = discord char limit
      a = 0
      if len(participants_formatted) > 1600:
        a = f"and {len(participants_formatted[1600:].split(', '))} others"
      participants_formatted = participants_formatted[:1600]
      participants_formatted= participants_formatted[:participants_formatted.rfind(",")] #don't combine the above line as .find will get wrong index. first shorten and assign  then find 
      content = f":tada:<:juuzou_gaming:1125994304528187392>**Giveaway Winner Announcement!**<:juuzou_gaming:1125994304528187392>:tada:\nThe winners are:\n**@{',<ENTERCHR101>@'.join(random.sample(participants, winners))}**\n\n:partying_face:Congratulations!!:partying_face:\n\nParticipants: ```{participants_formatted} {a}```".replace("<ENTERCHR101>", "\n")
    view = ConfirmWinners()
    message = await interaction.followup.send(content, ephemeral = True, view = view)
    view.message = message