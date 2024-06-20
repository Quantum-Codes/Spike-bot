import discord, random, json
from main import guild_ids
from components.buttons import ConfirmWinners
from components.modals import GetWinnersCount


class message_commands(discord.Cog):
    def __init__(self, bot):
        self.bot = bot

    @discord.message_command(name="purge_react")
    async def purge_reacts(self, ctx, message):
        await ctx.defer(ephemeral=True)
        reacts = message.reactions[0]
        users = ""
        async for user in reacts.users():
            if not (
                user.get_role(1172086259599032400) is not None
                or user.get_role(1147788479732920401) is not None
                or user.get_role(1147788523244617791) is not None
                or user.get_role(1149505311619678258) is not None
            ):
                await message.remove_reaction(reacts, user)
        await ctx.followup.send("op")


def setup(bot):
    bot.add_cog(message_commands(bot))
