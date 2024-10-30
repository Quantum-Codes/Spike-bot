import discord
from main import guild_ids
from discord.commands import SlashCommandGroup
from db import db, funcs

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
    async def push_event_maker(self, ctx: discord.ApplicationContext, message: str):
        await db.create_push_event(
            str(ctx.guild_id),
            {
                "join_req_type": "total_trophy",
                "join_req": 10000
            }
        )
        await ctx.send(message)
    
    @push_event.command(name="join", description="Join an active push event")
    async def push_event_joinleave(self, ctx: discord.ApplicationContext, player_id: str = ""):
        await ctx.defer()
        if not player_tag:
            data = await db.get_player_tag(ctx.author.id)
            if data is None:
                await ctx.respond(embed=await funcs.TagNotFoundEmbed(mode="save"))
                return
            player_tag = data
        else:
            player_tag = funcs.fix_tag(player_tag)
        
        await db.join_leave_push_event(
            str(ctx.guild_id), 
            str(ctx.author.id),
            {
                "total_trophies": 10101
            }
        )
        


def setup(bot):
    bot.add_cog(push_event_commands(bot))
