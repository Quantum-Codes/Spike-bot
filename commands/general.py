import discord, discord.ext, time
from discord.commands import SlashCommandGroup
from main import guild_ids
from db import db, funcs, Colour
from components.buttons import GiveawayJoin, ConfirmWinners
from commands.brawlstars import bs_api


class giveawaycommands(discord.Cog):
    def __init__(self, bot):
        self.bot = bot

    giveaway = SlashCommandGroup("giveaway", "Handle giveaways.", guild_ids=guild_ids)

    async def cog_command_error(self, ctx, error):
        print(error, error.__cause__, type(error))
        if isinstance(error, discord.ext.commands.MessageNotFound):
            await ctx.respond(
                "Message not found. Check the message ID and try again.", ephemeral=True
            )
        else:
            raise error

    @giveaway.command(name="create", description="Host a giveaway")
    @discord.ext.commands.has_permissions(administrator=True)
    async def giveaway_maker(self, ctx, message: str, winners: int):
        await ctx.defer(ephemeral=True)
        msg = await ctx.send(
            embed=discord.Embed(description=await funcs.replace_placeholders(message, ctx)),
            view=GiveawayJoin(),
        )
        await db.create_giveaway(msg.id, ctx.channel.id, winners)
        await ctx.followup.send("Success", ephemeral=True)

    @giveaway.command(name="end", description="Ends a giveaway")
    @discord.ext.commands.has_permissions(administrator=True)
    async def giveaway_end(self, ctx, messageid: discord.Message, reward: str):
        await ctx.defer(ephemeral=True)
        message = messageid  # alias
        if not await db.check_valid_giveaway(message.id):
            await ctx.followup.send("not valid giveaway", ephemeral=True)
            return

        data = await db.end_giveaway(message.id)
        title = f"The giveaway of **__{reward}__** for {data['winners_count']} winners has come to an end and"
        content = (
            f"## 🎊<:juuzou_gaming:1125994304528187392>Giveaway Winner Announcement!<:juuzou_gaming:1125994304528187392>🎊\n{title} \n\n🥳The winners are:\n**<@!{'> ,<ENTERCHR101><@!'.join([str(ab['user_id']) for ab in data['winners']])}>**!!🥳\n\n:tada:Congratulations!!:tada:\n\n`Participants: {data['participants_count']}`".replace(
                "<ENTERCHR101>", "\n"
            )
            if data["winners_count"] != 0
            else "Nobody won... 0 participants"
        )
        view = ConfirmWinners(message)
        message = await ctx.followup.send(
            embed=discord.Embed(colour=discord.Colour.green(), description=content),
            ephemeral=True,
            view=view,
        )
        view.message = message  # to pass context

    @giveaway.command(
        name="cleanup",
        description="⚠️Deletes all data related to giveaway⚠️ Don't use unless no further rerolls required",
    )
    @discord.ext.commands.has_permissions(administrator=True)
    async def giveaway_cleanup(self, ctx, messageid: discord.Message, confirm: bool):
        if not confirm:
            await ctx.respond("Cancelled cleanup.", ephemeral=True)
            return

        await ctx.defer(ephemeral=True)

        message = messageid  # alias
        if not await db.check_valid_giveaway(message.id):
            await ctx.followup.send("not valid giveaway", ephemeral=True)
            return

        await db.cleanup_giveaway(ctx, message.id)
        await ctx.followup.send(
            f"Deleted all data related to the giveaway with **ID: {message.id}**"
        )

    @giveaway_cleanup.error
    @giveaway_end.error
    @giveaway_maker.error
    async def giveaway_errorhandler(self, ctx, error):
        if isinstance(error, discord.ext.commands.CheckFailure):
            await ctx.respond(
                f"Missing permissions: `{', '.join(error.missing_permissions)}`",
                ephemeral=True,
            )


class utilitycommands(discord.Cog):
    def __init__(self, bot):
        self.bot = bot

    utility = SlashCommandGroup("utility", "Server enhancers")
    welcome = utility.create_subgroup("welcome", "Welcomer commands")
    autokick = utility.create_subgroup("autokick", "Autokick module commands")

    async def cog_command_error(self, ctx, error):
        print(error, error.__cause__, type(error))
        if isinstance(error, discord.ext.commands.MessageNotFound):
            await ctx.respond(
                "Message not found. Check the message ID and try again.", ephemeral=True
            )
        else:
            raise error

    @discord.slash_command(
        name="servers", description="list out servers I'm in", guild_ids=guild_ids
    )
    @discord.ext.commands.is_owner()
    async def serverscommand(self, ctx):
        await ctx.respond("\n".join(guild.name for guild in self.bot.guilds))
        
    @discord.slash_command(
        name="kill", description="shut down bot", guild_ids=[1017417232952852550]
    )
    @discord.ext.commands.is_owner()
    async def killbot(self, ctx):
        await db.close_db()
        await ctx.respond("closed all processes")

    @serverscommand.error
    async def serverscommanderror(self, ctx, error):
        await ctx.respond("bot owner only command..")

    @welcome.command(name="setup", description="Set welcome message channel")
    @discord.ext.commands.has_permissions(administrator=True)
    async def welcomer(
        self,
        ctx,
        channel: discord.TextChannel,
        message: str,
        colour: Colour = int("0x2ecc71", 16),
        embed_title: str = "",
        ping_member: bool = True,
        image_url: str = "",
        thumb_url: str = "",
    ):
        await ctx.defer()
        # add url validation, color option and validation
        embed = discord.Embed(
            colour=discord.Colour(colour),
            title="Saved welcome message",
            description=message,
        )
        embed.add_field(name="channel", value=f"<#{channel.id}>")
        embed.add_field(name="title", value=embed_title if embed_title else "not set")
        embed.add_field(
            name="ping new member", value="True" if ping_member else "False"
        )
        embed.add_field(name="image", value=image_url if image_url else "not set")
        embed.add_field(name="thumbnail", value=thumb_url if thumb_url else "not set")
        embed.set_footer(
            text="Use `/utility welcome test_message` to preview the message"
        )
        await db.save_server_settings(
            ctx.guild.id,
            "welcomer",
            {
                "message": message,
                "channel": str(channel.id),  # json cant hangle bigints. so store as str
                "title": embed_title,
                "ping": ping_member,
                "image_url": image_url,
                "thumb_url": thumb_url,
                "colour": colour,
            },
        )
        await ctx.followup.send(embed=embed)

    @discord.slash_command(name="ping", description="bot latency including a db query")
    async def ping_time(self, ctx):
        await ctx.defer()
        t1 = time.time()
        await db.get_server_settings(ctx.guild.id)  # just run a query
        t1 = time.time() - t1
        t2 = time.time()
        async with bs_api() as api:
            await api.get_player("#28PUJ2VP9")
        t2 = time.time() - t2
        await ctx.followup.send(f"Ping: {self.bot.latency}s\nQuery: {t1}s\nAPI: {t2}s")

    @welcome.command(name="test_message", description="Test the welcome message")
    @discord.ext.commands.has_permissions(administrator=True)
    async def welcometest(self, ctx):
        data = await db.get_server_settings(ctx.guild.id, "welcomer")
        if data is None:
            embed = discord.Embed(
                colour=discord.Colour.red(),
                description="No welcome message set for this server.\nSet it up using `/utility welcome setup` command.",
            )
            await ctx.respond(embed=embed)
            return
        embed = discord.Embed(
            colour=discord.Colour(data["colour"]),
            title=await funcs.replace_placeholders(data["title"], ctx),
            description=await funcs.replace_placeholders(data["message"], ctx),
        )
        embed.add_field(
            name="would have been posted in:", value=f"<#{data['channel']}>"
        )
        embed.set_image(
            url=await funcs.replace_placeholders(data["image_url"], ctx, image_url=True)
        )
        embed.set_thumbnail(
            url=await funcs.replace_placeholders(data["thumb_url"], ctx, image_url=True)
        )
        await ctx.respond(f"{ctx.user.mention}" if data["ping"] else None, embed=embed)

    @welcome.command(name="remove", description="Disable and delete welcome message")
    @discord.ext.commands.has_permissions(administrator=True)
    async def removewelcome(self, ctx):
        await ctx.defer()
        data = await db.get_server_settings(ctx.guild.id, "welcomer")
        if data is None:
            embed = discord.Embed(
                colour=discord.Colour.red(),
                description="No welcome message set for this server.\nSet it up using `/utility welcome setup` command.",
            )
            await ctx.followup.send(embed=embed)
            return

        await db.delete_server_settings(ctx.guild.id, "welcomer")
        embed = discord.Embed(
            colour=discord.Colour.red(),
            title="Deleted welcome message",
            description=data["message"],
        )
        embed.add_field(
            name="title", value=data["title"] if data["title"] else "not set"
        )
        embed.add_field(
            name="image", value=data["image_url"] if data["image_url"] else "not set"
        )
        embed.add_field(
            name="thumbnail",
            value=data["thumb_url"] if data["thumb_url"] else "not set",
        )
        await ctx.followup.send(embed=embed)

    @autokick.command(name="setup", description="Kick newly created accounts")
    @discord.ext.commands.has_permissions(administrator=True)
    async def autokick_setup(self, ctx, age_in_seconds: int = 7 * 24 * 3600):
        await ctx.defer()
        embed = discord.Embed(
            colour=discord.Colour.green(),
            title="Autokick enabled",
            description=f"Any account younger than {age_in_seconds} seconds will be kicked when they join.\nTo disable, use `/utility autokick disable`",
        )
        await db.save_server_settings(ctx.guild.id, "autokick", {"age": age_in_seconds})
        await ctx.followup.send(embed=embed)

    @autokick.command(name="disable", description="Disable autokick")
    @discord.ext.commands.has_permissions(administrator=True)
    async def autokick_disable(self, ctx):
        await ctx.defer()
        if await db.get_server_settings(ctx.guild.id, "autokick") is None:
            embed = discord.Embed(
                colour=discord.Colour.red(),
                title="Autokick was not setup",
                description="Autokick was not setup for this server.\nEnable it using `/utility autokick setup`",
            )
            await ctx.followup.send(embed=embed)
            return

        await db.delete_server_settings(ctx.guild.id, "autokick")
        embed = discord.Embed(
            colour=discord.Colour.green(),
            title="Autokick is disabled",
            description="Autokick is now disabled for this server.\nYou may enable autokick again using `/utility autokick setup`",
        )
        await ctx.followup.send(embed=embed)

    @welcomer.error
    @removewelcome.error
    @welcometest.error
    async def errorhandler(self, ctx, error):
        if isinstance(error, discord.ext.commands.CheckFailure):
            await ctx.respond(
                f"Missing permissions: `{', '.join(error.missing_permissions)}`",
                ephemeral=True,
            )
        if isinstance(error, discord.ext.commands.BadArgument):
            if "Bad hex" in error.args:
                await ctx.respond(
                    "Must be a hex code(6 character code). eg `#ffffff`. Use a color picker: https://g.co/kgs/s8Wsnxt"
                )


def setup(bot):
    bot.add_cog(giveawaycommands(bot))
    bot.add_cog(utilitycommands(bot))
