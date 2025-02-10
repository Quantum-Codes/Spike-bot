import discord, math, csv
from main import guild_ids
from discord.commands import SlashCommandGroup
from db import db, funcs, bs_api
from io import StringIO

class push_event_commands(discord.Cog):
    def __init__(self, bot):
        self.bot = bot

    pushing_comms = SlashCommandGroup("push", "Handles push stats")
    push_event = pushing_comms.create_subgroup("event", "Push event commands")

    """async def cog_command_error(self, ctx, error):
        print(error, error.__cause__, type(error))
        if isinstance(error, discord.ext.commands.MessageNotFound):
            await ctx.respond(
                "Message not found. Check the message ID and try again.", ephemeral=True
            )
        else:
            raise error"""

    @push_event.command(name="create", description="Create a push event")
    @discord.ext.commands.has_permissions(administrator=True)
    async def push_event_maker(self, ctx: discord.ApplicationContext):
        load_msg = await ctx.respond(embed=await funcs.LoadingEmbed(), ephemeral=True)
        
        if (await db.check_valid_push_event(str(ctx.guild_id))):
            embed = discord.Embed(
                color=discord.Color.red(),
                title = "Failed creation",
                description=f"A push event is already active for this server.\nDelete it using `/push event delete`\n\nCreation command used now:\n`/push event create`"
            )
            await load_msg.edit(embed=embed)
            return
        
        await db.create_push_event(
            str(ctx.guild_id),
            {
                "join_req_type": "total_trophy",
                "join_req": 10000
            }
        )
        await load_msg.edit(content="Succesfully created push event. Members may join using `/push event join`.", embed=None)
    
    @push_event.command(name="join", description="Join an active push event")
    async def push_event_join(self, ctx: discord.ApplicationContext, player_tag: str = ""):
        load_msg = await ctx.respond(embed=await funcs.LoadingEmbed())
        if not player_tag:
            data = await db.get_player_tag(ctx.author.id)
            if data is None:
                await load_msg.edit(embed=await funcs.TagNotFoundEmbed(mode="save"))
                return
            player_tag = data
        else:
            player_tag = await funcs.fix_tag(player_tag)
        
        if not (await db.check_valid_push_event(str(ctx.guild_id))):
            await load_msg.edit(content = "No pushevent is active in this server.", embed = None)
            return

        if (await db.check_joined_push_event(str(ctx.guild_id), str(ctx.author.id))):
            await load_msg.edit(content = "You have already joined the event.", embed = None)
            return
        
        async with bs_api() as api:
            if (await api.get_player(player_tag)).status == 404:
                await load_msg.edit(embed = await funcs.TagNotFoundEmbed(player_tag=player_tag.replace("%23", "#")))
                return
            
        await db.join_leave_push_event(
            str(ctx.guild_id), 
            str(ctx.author.id),
            {
                "player_tag": player_tag # total trophies to be requested 5-10mins before start of event.
            },
            mode = "join"
        )
        embed = discord.Embed(colour=discord.Colour.green(), title="Joined push event", description="You have successfully joined the push event using account {}!".format(player_tag.replace("%23", "#")))
        embed.set_footer(text = "Joined by mistake? Leave using `/push event leave`\nJoined using wrong account? Leave then join using `push event join player_tag:#XXXXXXXX`")
        await load_msg.edit(embed=embed)
    
    @push_event.command(name="leave", description="Leave a push event")
    async def push_event_leave(self, ctx: discord.ApplicationContext):
        if not (await db.check_valid_push_event(str(ctx.guild_id))):
            await ctx.respond("No pushevent is active in this server.")
            return
        
        if not (await db.check_joined_push_event(str(ctx.guild_id), str(ctx.author.id))):
            await ctx.respond("You are not participating in this event.")
            return
        
        await db.join_leave_push_event(
            str(ctx.guild_id), 
            str(ctx.author.id),
            mode = "leave"
        )
        embed = discord.Embed(colour=discord.Colour.green(), title="Left push event", description="You have successfully left the push event!")
        embed.set_footer(text = "Want to join back? Join using `/push event join`")
        await ctx.respond(embed=embed)
    

    @push_event.command(name="start", description="Start a push event")
    @discord.ext.commands.has_permissions(administrator=True)
    async def push_event_starter(self, ctx: discord.ApplicationContext):
        load_msg = await ctx.respond(embed=await funcs.LoadingEmbed())
        
        if not (await db.check_valid_push_event(str(ctx.guild_id))):
            await load_msg.edit(content = "No active push event.", embed = None)
            return
        
        embedtext = await db.start_push_event(str(ctx.guild_id))
        embed = discord.Embed(
            color=discord.Color.green(), 
            title = "Push Event Started",
            description= f"Push event has started!\nGet busy pushing your trophies till the end of the event!\n\n{embedtext}"
        )
        embed.set_footer(text="Note that change in trophies count. Total trophies do not matter unless a tie exists where person with more total trophies or more brawler trophies win depending on context.")
        await load_msg.edit(embed = embed)
    
    async def generate_push_leaderboards(self, guild_id: str):
        data = await db.status_push_event(guild_id)
        embedtext = "**User       --     <:trophy:1149687899336482928> Trophy delta**\n"
        count = len(data)
        sno_len = int(math.log10(count)) if count > 0 else 1
        
        for i in range(min(25, count)):
            embedtext += f"{str(i).zfill(sno_len)}. <@!{data[i][0]}>  --  <:trophy:1149687899336482928> {data[i][1]}\n" # make this pagewise zfill eventually (1st page 0-50. so 01 02 03.)
        
        with StringIO(newline="\n") as csv_file:
            csv_writer = csv.writer(csv_file)
            csv_writer.writerow(["User", "Trophy delta", "Start trophies", "End trophies"])
            csv_writer.writerows(data)
            csv_file.flush()
            csv_file.seek(0)
            file = discord.File(csv_file, filename="push_event.csv")
        
        if count == 0:
            embedtext = "Nobody... \:("
        
        return embedtext, file, count
    
    @push_event.command(name="status", description="Show current progress of push event")
    @discord.ext.commands.has_permissions(administrator=True)
    async def push_event_status(self, ctx: discord.ApplicationContext):
        load_msg = await ctx.respond(embed=await funcs.LoadingEmbed())
        
        if not (await db.check_valid_push_event(str(ctx.guild_id))):
            await load_msg.edit(content = "No active push event.", embed=None)
            return
        
        embedtext, file, count = await self.generate_push_leaderboards(str(ctx.guild_id))
        
        embed = discord.Embed(
            color=discord.Color.green(), 
            title = "Push Event Progress",
            description= f"## Top 25 Leaderboards:\n\n{embedtext}"
        )
        
        if count > 25:
            embed.set_footer(text="Full leaderboard can be seen through the attached csv file (can use excel to view)")
        
        
        await load_msg.edit(embed=embed, files=[file] if count > 25 else [])
    
    
    @push_event.command(name="end", description="End a push event and display winners")
    @discord.ext.commands.has_permissions(administrator=True)
    async def push_event_ender(self, ctx: discord.ApplicationContext):
        load_msg = await ctx.respond(embed=await funcs.LoadingEmbed())
        
        if not (await db.check_valid_push_event(str(ctx.guild_id))):
            await load_msg.edit(content = "No active push event.", embed=None)
            return
        
        embedtext, file, count = await self.generate_push_leaderboards(str(ctx.guild_id))
        
        embed = discord.Embed(
            color=discord.Color.green(), 
            title = "Push Event Ended!",
            description= f"The push event has ended! Here are the leaderboards:\n## Top 25 final Leaderboards:\n\n{embedtext}"
        )
        embed.set_footer(text="Full leaderboard can be seen through the attached file below (csv format, can use excel to view)")
        
    
        await load_msg.edit(embed=embed, file=file)
        await db.delete_push_event(str(ctx.guild_id))

def setup(bot):
    bot.add_cog(push_event_commands(bot))
