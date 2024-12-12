import discord
from db import funcs
from main import guild_ids


class RoleStats(discord.Cog):
    def __init__(self, bot):
        self.bot = bot

    @discord.slash_command(
        name="role_count", description="GET role member count", guild_ids=guild_ids
    )
    async def role_count(
        self,
        ctx,
        role1: discord.Role,
        title: str = "Role stats",
        role2: discord.Role = None,
        role3: discord.Role = None,
        role4: discord.Role = None,
        role5: discord.Role = None,
        role6: discord.Role = None,
        role7: discord.Role = None,
        role8: discord.Role = None,
        role9: discord.Role = None,
        role10: discord.Role = None,
    ):
        load_msg = await ctx.respond(embed=await funcs.LoadingEmbed())
        embed = discord.Embed(
            title=title,
            color=discord.Colour.blurple(),
        )
        for role in [
            role1,
            role2,
            role3,
            role4,
            role5,
            role6,
            role7,
            role8,
            role9,
            role10,
        ]:
            if not role:
                continue
            embed.add_field(name=role.name, value=len(role.members))
        await load_msg.edit(embed=embed)


def setup(bot):
    bot.add_cog(RoleStats(bot))
