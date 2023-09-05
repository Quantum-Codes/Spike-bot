import discord

#confirm_repeat button in commands/webhook.py
class ConfirmWinners(discord.ui.View):
    @discord.ui.button(label= "Confirm", style=discord.ButtonStyle.primary, emoji=None)
    async def button_callback(self, button, interaction):
      button.disabled = True
      button.label = "Approved."
      button.style = discord.ButtonStyle.success
      await interaction.response.edit_message(view=self)
      await interaction.followup.send(interaction.message.content)