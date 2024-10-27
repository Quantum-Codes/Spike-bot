import discord
from main import guild_ids
from discord.commands import SlashCommandGroup

class push_event_commands(discord.Cog):
    def __init__(self, bot):
        self.bot = bot

    pushing_comms = SlashCommandGroup("push", "Handles push stats", guild_ids=guild_ids)
    push_event = pushing_comms.create_subgroup("event", "Push event commands", guild_ids=guild_ids)

    async def cog_command_error(self, ctx, error):
        print(error, error.__cause__, type(error))
        if isinstance(error, discord.ext.commands.MessageNotFound):
            await ctx.respond(
                "Message not found. Check the message ID and try again.", ephemeral=True
            )
        else:
            raise error

    @push_event.command(name="create", description="Create a push event")
    @discord.ext.commands.has_permissions(administrator=True)
    async def push_event_maker(self, ctx, message: str, winners: int):
        await ctx.defer(ephemeral=True)


def setup(bot):
    bot.add_cog(push_event_commands(bot))
