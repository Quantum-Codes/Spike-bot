import discord, requests, os, asyncio, aiohttp
from db import db, funcs, bs_api
from main import guild_ids
from discord.commands import SlashCommandGroup
    

async def get_battledata(player_tag, player=None):
    async with bs_api() as api:
        player_tag = await funcs.fix_tag(player_tag)
        data = await api.get_battlelog(player_tag)
        if data.status == 200:
            data = await data.json()
            if not player:
                # if we already have player object, then no need to request again
                player = await api.get_player(player_tag)
                player = await player.json()
        elif data.status == 404:
            data = await data.json()
            reason = data.get("reason")
            if reason == "notFound":
                return 404
        else:
            return 500

    raw_stats = {"victory": 0, "defeat": 0, "draw": 0, "starplayer": 0}
    # print(data['items'][0]['battle'].keys())
    for item in data["items"]:
        #  print(item)
        battleresult = item["battle"].get("result")
        if battleresult is None:  # showdown
            battleresult = item["battle"].get("rank")
            if battleresult is None:
                print(item)
                continue
            battleresult = (
                "victory"
                if battleresult <= (2 if item["battle"]["mode"] == "duoShowdown" else 4)
                else "defeat"
            )  # since lonestar, takedown also has 4 winners. so on else clause
        if raw_stats.get(battleresult) is not None:
            raw_stats[battleresult] += 1
            if battleresult == "victory":
                starplayer = item["battle"].get("starPlayer")
                if starplayer is None:
                    if "Showdown" in item["battle"]["mode"]:
                        if item["battle"]["rank"] <= (
                            1 if "duo" in item["battle"]["mode"] else 2
                        ):
                            raw_stats["starplayer"] += 1
                else:
                    if (
                        item["battle"]["starPlayer"]["tag"].upper()
                        == player["tag"].upper()
                    ):
                        raw_stats["starplayer"] += 1
        else:
            raw_stats.setdefault(battleresult, 1)
    stats = {}
    raw_stats2 = raw_stats.copy()
    raw_stats2.pop("starplayer")
    total_matches = sum(raw_stats2.values())
    for k, v in raw_stats.items():
        if k == "starplayer":
            stats[k + "_rate"] = (
                int(round(v / raw_stats["victory"], 4) * 10000) / 100
            )  # round doesn't do its job properly
        else:
            stats[k + "_rate"] = int(round(v / total_matches, 4) * 10000) / 100

    return (player, stats)


async def embed_player(data, battle_data):
    embed = discord.Embed(
        title=f"{data['name']}",
        color=int(data["nameColor"][4:], base=16),
    )
    embed.add_field(name="Trophies", value=data["trophies"])
    embed.add_field(name="Highest Trophies", value=data["highestTrophies"], inline=True)
    embed.add_field(name="Exp Level", value=data["expLevel"], inline=True)

    embed.add_field(name="3v3 wins", value=data["3vs3Victories"])
    embed.add_field(name="solo wins", value=data["soloVictories"], inline=True)
    embed.add_field(name="duo wins", value=data["duoVictories"], inline=True)

    if battle_data is not None:
        embed.add_field(
            name="Recent Win rate", value=str(battle_data["victory_rate"]) + "%"
        )
        embed.add_field(
            name="Recent starplayer rate",
            value=str(battle_data["starplayer_rate"]) + "%",
            inline=True,
        )
        embed.add_field(
            name="Recent loss rate",
            value=str(battle_data["defeat_rate"]) + "%",
            inline=True,
        )  # replace this if space needed
    else:
        embed.add_field(name="Recent Win rate", value="Error")
        embed.add_field(name="Recent starplayer rate", value="Error")
        embed.add_field(name="Recent loss rate", value="Error")

    embed.add_field(
        name="Champtionship Challenge",
        value=(
            "Qualified this month"
            if data["isQualifiedFromChampionshipChallenge"]
            else "Not Qualified this month"
        ),
    )

    if data["club"].get("name") is not None:  # check if joined club
        embed.add_field(name="Club name", value=data["club"]["name"], inline=True)
    else:
        embed.add_field(name="Club name", value="No club joined", inline=True)

    embed.set_thumbnail(
        url=f"https://cdn.brawlify.com/profile-icons/regular/{data['icon']['id']}.png"
    )
    return embed


async def embed_club(data):
    embed = discord.Embed(
        title=f"{data['name']}",
        color=discord.Color.brand_green(),
        description=data["description"],
    )
    embed.add_field(name="Trophies", value=data["trophies"])
    embed.add_field(name="Type", value=data["type"], inline=True)
    embed.add_field(
        name="Required Trophies", value=data["requiredTrophies"], inline=True
    )

    roles = {"senior": 0, "member": 0, "vicePresident": 0}
    president = None
    for item in data["members"]:
        if item["role"] == "president":
            president = item["name"]
            continue
        roles[item["role"]] += 1

    embed.add_field(name="President", value=president)
    embed.add_field(
        name="Average Trophies",
        value=round(data["trophies"] / len(data["members"]), 2),
        inline=True,
    )

    embed.add_field(name="Vice Presidents", value=roles["vicePresident"])
    embed.add_field(name="Seniors", value=roles["senior"], inline=True)
    embed.add_field(name="Members", value=roles["member"], inline=True)

    embed.set_thumbnail(url=f"https://cdn.brawlify.com/club-badges/regular/{data['badgeId']}.png")
    return embed


class brawl(discord.Cog):
    def __init__(self, bot):
        self.bot = bot

    tagcommands = SlashCommandGroup("tag", "Handle playertags")

    @discord.slash_command(name="playerstats", description="GET a player's stats")
    async def playerstats(self, ctx, player_tag: str = ""):
        load_msg = await ctx.respond(embed=await funcs.LoadingEmbed())
        async with bs_api() as api:
            if not player_tag:
                data = await db.get_player_tag(ctx.author.id)
                if data is None:
                    await load_msg.edit(embed=await funcs.TagNotFoundEmbed(mode="save"))
                    return
                player_tag = data
            player_tag = await funcs.fix_tag(player_tag)
            data = await api.get_player(player_tag)
            if data.status == 200:
                data = await data.json()
                battle_data = await get_battledata(player_tag, data)
                if type(battle_data) is int:
                    battle_data = None
                else:
                    battle_data = battle_data[1]
                await load_msg.edit(embed=await embed_player(data, battle_data))
            elif data.status == 404:
                data = await data.json()
                reason = data.get("reason")
                if reason == "notFound":
                    await load_msg.edit(content = "No such player exists", embed=None)
            else:
                await load_msg.edit(content = f"error {data.status}", embed = None)
                print(vars(data), data)

    @discord.slash_command(name="clubstats", description="GET a club's stats")
    async def clubstats(self, ctx, club_tag: str = None):
        load_msg = await ctx.respond(embed=await funcs.LoadingEmbed())
        async with bs_api() as api:
            if club_tag is None:
                # get player's club here
                data = await db.get_player_tag(ctx.author.id)
                if data is None:
                    await load_msg.edit(embed=await funcs.TagNotFoundEmbed(mode="save"))
                    return
                player_tag = data
                # assumed if tag saved in db then its valid
                playerdata = await api.get_player(player_tag)
                playerdata = await playerdata.json()
                club_tag = playerdata["club"].get("tag")
                if club_tag is None:
                    await load_msg.edit(
                        "You are not part of a club... Use the `club_tag` parameter to see stats of a specific club.", embed=None
                    )
                    return
            club_tag = await funcs.fix_tag(club_tag)
            data = await api.get_club(club_tag)
            if data.status == 200:
                data = await data.json()
                await load_msg.edit(embed=await embed_club(data))
            elif data.status == 404:
                data = await data.json()
                reason = data.get("reason")
                if reason == "notFound":
                    await load_msg.edit(content = "No such club exists", embed = None)
            else:
                await load_msg.edit(content = f"error {data.status}", embed = None)

    @discord.slash_command(
        name="battlestats", description="GET a player's battle stats"
    )
    async def battlestats(self, ctx, player_tag: str = ""):
        load_msg = await ctx.respond(embed=await funcs.LoadingEmbed())
        if not player_tag:
            data = await db.get_player_tag(ctx.author.id)
            if data is None:
                await load_msg.edit(embed=await funcs.TagNotFoundEmbed(mode="save"))
                return
            player_tag = data
        data_raw = await get_battledata(player_tag)
        if type(data_raw) is not int:
            player, data = data_raw
            message = f"# {player['name']}'s stats\n"
            message += "\n".join([f"**{I[0]}**: {I[1]}" for I in data.items()])
            embed = discord.Embed(
                title=f"{player['name']}'s stats", color=discord.Colour.dark_gold()
            )
            for k, v in data.items():
                embed.add_field(name=k, value=str(v) + "%")
            embed.set_footer(text="Data from last 25 matches")

            await load_msg.edit(embed=embed)
        elif data_raw == 404:  # also 404 with modded accs
            await load_msg.edit(
                "No such player exists OR this player hasn't played any battles...", embed = None
            )
        else:
            await load_msg.edit(content = f"error {data.status}", embed = None)

    @tagcommands.command(name="save", description="Save your player tag")
    async def save_tag(self, ctx, player_tag: str):
        embed = discord.Embed(colour=discord.Colour.yellow())
        async with bs_api() as api:
            player_tag = await funcs.fix_tag(player_tag)
            # currently no verification system on tags. so duplicate checking is waste.
            # sql.execute("SELECT user_id FROM spikebot_users WHERE player_tag = %s;") #duplicate tag checker.
            # if sql.rowcount != 0:
            #  await ctx.respond("Duplicate")
            with ctx.channel.typing():
                data = await api.get_player(player_tag)
            if data.status == 200:
                data = await data.json()
                embed.add_field(
                    name="Confirmation:",
                    value=f"Are you {data['name']}? React with 👍 or 👎.\n You have 2mins to do so.",
                )
                bot_msg = await ctx.respond(embed=embed)
            elif data.status == 404:
                await ctx.respond(embed=await funcs.TagNotFoundEmbed(mode="404", player_tag=player_tag.replace("%23", "#")))
                return
            else:
                await ctx.respond(f"error {data.status}")
                return

        def check(reaction, user):
            return user == ctx.author and str(reaction.emoji) in ("👍", "👎")

        try:
            m = await bot_msg.original_response()
            await m.add_reaction("👍")
            await m.add_reaction("👎")
            embed.fields = []  # clear for future usage
            reaction, user = await self.bot.wait_for(
                "reaction_add", timeout=120.0, check=check
            )
        except asyncio.TimeoutError:
            embed.colour = discord.colour.red()
            embed.fields = []  # just in case since in except loop
            embed.add_field(
                name="Timeout",
                value="you took too long.. try using command again...",
            )
            await ctx.send(embed=embed)
            return

        if str(reaction.emoji) == "👎":
            embed.add_field(name="Cancelled.", value="")
            embed.colour = discord.Colour.red()
            await ctx.respond(embed=embed)
            return

        await db.add_user(ctx.author.id, player_tag)

        embed.colour = discord.Colour.green()
        embed.add_field(name="Saved tag:", value=player_tag.replace("%23", "#"))
        embed.set_footer(text="To check your tag, use `/tag show`")
        await ctx.respond(embed=embed)

    @tagcommands.command(name="remove", description="Delete your player tag")
    async def delete_tag(self, ctx):
        player_tag = await db.get_player_tag(ctx.author.id)
        if not player_tag:
            await ctx.respond(
                "You haven't saved a tag yet. If you want to save your tag instead,  use `/tag save` command."
            )
            return
        await db.update_tag(ctx.author.id, None)
        await ctx.respond(
            "Removed tag successfully.\n To save your tag again, use `/tag save` command."
        )

    @tagcommands.command(name="show", description="Check your player tag")
    async def show_tag(self, ctx):  # , user: discord.User = None):
        embed = discord.Embed(colour=discord.Colour.yellow())
        data = await db.get_player_tag(ctx.author.id)
        """
    if user:
        if ctx.author.get_role(1208026724399321120): # tournament manager role ID at juuzou server 
            data = await db.get_player_tag(user.id)
        else:
            await ctx.respond("Don't use this option", ephemeral=True)
            return 
    """
        if not data:
            await ctx.respond(embed=await funcs.TagNotFoundEmbed(mode="save"))
            return
        else:
            embed.colour = discord.Colour.green()
            embed.add_field(name="Your tag:", value=data.replace("%23", "#"))
            embed.set_footer(
                text="If the tag is not yours, either replace it with `/tag save` Or completely remove it by using `/tag remove` command. "
            )
            await ctx.respond(embed=embed)
            return


def setup(bot):
    bot.add_cog(brawl(bot))
