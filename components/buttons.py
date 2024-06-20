import discord
from db import db


class ConfirmWinners(discord.ui.View):
    def __init__(self, message):
        self.gaw_msg = message
        super().__init__(timeout=240)

    async def on_timeout(self):
        self.disable_all_items()
        await self.message.edit(
            ":warning:You took longer than 4 minutes. Buttons disabled.:warning:\n"
            + self.message.content,
            view=self,
        )

    @discord.ui.button(label="Confirm", style=discord.ButtonStyle.primary, emoji=None)
    async def confirm_callback(self, button, interaction):
        self.disable_all_items()
        button.label = "Approved."
        button.style = discord.ButtonStyle.success
        await interaction.response.edit_message(view=self)
        await interaction.channel.send(
            interaction.message.content, embed=interaction.message.embeds[0]
        )
        await interaction.followup.send(
            f"Use giveaway cleanup command to delete data about the giveaway. Only use if no more rerolls required.\nData is autmatically cleared after 30 days of ending.",
            ephemeral=True,
        )

    @discord.ui.button(label="Cancel", style=discord.ButtonStyle.danger, emoji=None)
    async def cancel_callback(self, button, interaction):
        self.disable_all_items()
        button.label = "Cancelled."
        button.style = discord.ButtonStyle.gray
        await interaction.response.edit_message(view=self)
        await interaction.followup.send(
            "Trigger giveaway end command again to choose new winners.", ephemeral=True
        )


class GiveawayLeave(discord.ui.View):
    def __init__(self, msgid):
        super().__init__(timeout=60)
        self.msgid = msgid

    async def on_timeout(self):
        self.disable_all_items()
        await self.msg.edit(
            ":warning:You took longer than 1 minute. Buttons disabled.:warning:\n"
            + self.msg.content,
            view=self,
        )

    @discord.ui.button(
        style=discord.ButtonStyle.danger, label="Leave giveaway", emoji="⚠️"
    )
    async def leave_callback(self, button, interaction):
        self.disable_all_items()
        await db.join_leave_giveaway(self.msgid, interaction.user.id, mode="leave")
        await interaction.response.edit_message(
            content="Successfully left giveaway.", view=self
        )


class GiveawayJoin(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)  # persistent view

    @discord.ui.button(
        label="Join Giveaway",
        style=discord.ButtonStyle.primary,
        emoji="🎁",
        custom_id="meisid2",
    )
    async def join_callback(self, button, interaction):
        await interaction.response.defer(ephemeral=True)

        if not await db.check_valid_giveaway(interaction.message.id):
            await interaction.followup.send(
                "Giveaway already ended or is invalid.", ephemeral=True
            )
            return
        if await db.check_joined_giveaway(interaction.message.id, interaction.user.id):
            msgview = GiveawayLeave(msgid=interaction.message.id)
            m = await interaction.followup.send(
                "You have already joined the giveaway.", ephemeral=True, view=msgview
            )
            msgview.msg = m
            return

        await db.join_leave_giveaway(
            interaction.message.id, interaction.user.id, mode="join"
        )
        await interaction.followup.send("Joined the giveaway!", ephemeral=True)
