import discord.ui, discord.ext, discord
import os, random, json, dotenv, re, asyncio, supabase
import aiomysql

dotenv.load_dotenv()


class database:
    def __init__(self):
        # connects to the database
        pass

    @classmethod
    async def create(cls):
        self = cls()
        """self.sup_db = await supabase.acreate_client(
            os.environ["sup_url"], os.environ["sup_key"]
        )"""
        self.db = await aiomysql.connect(user="u43452_T8oykA1YfD", password="UJAnbY=3RwBrbI+rl@N4O@Cn", host ="mysql.db.bot-hosting.net", port = 3306, db = "s43452_spikebot")
        self.sql = await self.db.cursor()
        return self

    async def db(self):
        return self.db
    
    async def close_db(self):
        await self.sql.close()
        self.db.close() #not a coro idk how

    async def get_server_settings(self, serverid, setting_type=None):
        if setting_type is None:
            """result = (
                await self.sup_db.table("server_settings")
                .select("type, data")
                .eq("server_id", serverid)
                .execute()
            )
            result = result.data"""
            await self.sql.execute("SELECT type, data FROM server_settings WHERE server_id = %s;", (serverid,))
            result = await self.sql.fetchall()
            print(result)
            data = [(item[0], item[1]) for item in result]
            return data if data else None
        """data = (
            await self.sup_db.table("server_settings")
            .select("data")
            .eq("server_id", serverid)
            .eq("type", setting_type)
            .execute()
        )
        data = data.data"""
        await self.sql.execute("SELECT data FROM server_settings WHERE server_id = %s AND type = %s;", (serverid, setting_type))
        data = await self.sql.fetchall()
        if data:  # non empty list= True
            data = data[0][0]  # guaranteed to be list of 1 element, so take just the 1st one
        else:
            data = None
        return data

    async def save_server_settings(self, serverid, setting_type, data):
        if await self.get_server_settings(serverid, setting_type) is None:
            """await self.sup_db.table("server_settings").insert(
                {"server_id": serverid, "type": setting_type, "data": data}
            ).execute()"""
            await self.sql.execute("INSERT INTO server_settings (server_id, type, data) VALUES (%s, %s, %s);", (serverid, setting_type, json.dumps(data)))
            await self.db.commit()
            return
        """await self.sup_db.table("server_settings").update({"data": data}).eq(
            "server_id", serverid
        ).eq("type", setting_type).execute()"""
        await self.sql.execute("UPDATE server_settings SET data = %s WHERE server_id = %s AND type = %s;", (json.dumps(data), serverid, setting_type))
        await self.db.commit()

    async def delete_server_settings(self, serverid, setting_type):
        """Always check if record exists before deleting

        Args:
            serverid (int): ServerID
            setting_type (str): Settingtype - may be autokick or welcomer
        """
        await self.sql.execute("DELETE FROM server_settings WHERE server_id = %s AND type = %s;", (serverid, setting_type))
        await self.db.commit()

    async def get_player_tag(self, discordid, check_deleted=False):
        """
        `check_deleted` is used internally to test if a player has his tag deleted (used in add_user func)
        """
        """data = (
            await self.sup_db.table("users")
            .select("player_tag")
            .eq("user_id", discordid)
            .execute()
        )"""
        await self.sql.execute("SELECT player_tag FROM users WHERE user_id = %s;", (discordid,))
        data = await self.sql.fetchall()
        if self.sql.rowcount == 0:
            if check_deleted:
                return None, False
            else:
                return None
        tag = data[0][0]
        if check_deleted:
            return tag, bool(tag is None)
        else:
            return tag

    async def update_tag(self, discordid, player_tag=None):
        """await self.sup_db.table("users").update({"player_tag": player_tag}).eq(
            "user_id", discordid
        ).execute()"""
        await self.sql.execute("UPDATE users SET player_tag = %s WHERE user_id = %s;", (player_tag, discordid))
        await self.db.commit()

    async def add_user(self, discordid, player_tag=None):
        """
        Only `discordid` is required. All others are optional params. default = None
        """
        tag = await self.get_player_tag(discordid, check_deleted=True)
        if type(tag[0]) is str or tag[1]:
            await self.update_tag(discordid, player_tag)
            return
        """await self.sup_db.table("users").insert(
            {"user_id": discordid, "player_tag": player_tag}
        ).execute()"""
        await self.sql.execute("INSERT INTO users (user_id, player_tag) VALUES (%s, %s);", (discordid, player_tag))
        await self.db.commit()

    async def create_giveaway(self, messageid, channelid, winners):
        """
        All params required.
        `winners` = Number of winners
        `messageid` = Message id of bot-posted giveaway
        `channelid` = Channel id of giveaway message
        """
        """await self.sup_db.table("giveaway_list").insert(
            {"message_id": messageid, "winners": winners, "channel_id": channelid}
        ).execute()"""
        await self.sql.execute("INSERT INTO giveaway_list (message_id, winners, channel_id) VALUES (%s, %s, %s);", (messageid, winners, channelid))
        await self.db.commit()

    async def check_joined_giveaway(self, messageid, userid):
        """data = (
            await self.sup_db.table("giveaway_joins")
            .select("*")
            .eq("message_id", messageid)
            .eq("user_id", userid)
            .execute()
        )"""
        await self.sql.execute("SELECT * FROM giveaway_joins WHERE message_id = %s AND user_id = %s;", (messageid, userid))
        await self.sql.fetchone()
        return self.sql.rowcount  # tests truth value

    async def check_valid_giveaway(self, messageid):
        """data = (
            await self.sup_db.table("giveaway_list")
            .select("*")
            .eq("message_id", messageid)
            .execute()
        )"""
        await self.sql.execute("SELECT * FROM giveaway_list WHERE message_id = %s;", (messageid,))
        await self.sql.fetchone()
        return self.sql.rowcount  # tests truth value

    async def join_leave_giveaway(self, messageid, userid, mode="join"):
        if mode == "leave":
            """await self.sup_db.table("giveaway_joins").delete().eq(
                "message_id", messageid
            ).eq("user_id", userid).execute()"""
            await self.sql.execute("DELETE FROM giveaway_joins WHERE message_id = %s AND user_id = %s;", (messageid, userid))
            await self.db.commit()
        else:
            """await self.sup_db.table("giveaway_joins").insert(
                {"message_id": messageid, "user_id": userid}
            ).execute()"""
            await self.sql.execute("INSERT INTO gievaway_joins (message_id, user_id) VALUES (%s, %s);", (messageid, userid))
            await self.db.commit()

    async def cleanup_giveaway(self, ctx, messageid):
        """
        AWAIT THIS
        run after all rerolling and winner choosing done AND all prizes claimed.
        deletes all joins and giveaway data from db.
        """
        """await self.sup_db.table("giveaway_joins").delete().eq(
            "message_id", messageid
        ).execute()"""
        await self.sql.execute("DELETE FROM giveaway_joins WHERE message_id = %s;", (messageid,))
        """channelid = (
            await self.sup_db.table("giveaway_list")
            .delete()
            .eq("message_id", messageid)
            .execute()
        )"""
        await self.sql.execute("DELETE FROM giveaway_list WHERE message_id = %s;", (messageid,))
        channelid = await self.sql.fetchone()
        channelid = channelid[2]
        channel = ctx.guild.get_channel(channelid)
        message = await channel.fetch_message(messageid)
        view = discord.ui.View.from_message(message)
        view.disable_all_items()
        await message.edit(view=view)
        await self.db.commit()

    async def end_giveaway(self, messageid):
        """
        Does not edit/delete db. Only reads to db
        Return value: dict. (keys: winners, winners_count, participants, participants_count)
        participants, winners -> list of single item tuples with discord ID (int) inside them.
        """
        """participants = (
            await self.sup_db.table("giveaway_joins")
            .select("user_id")
            .eq("message_id", messageid)
            .execute()
        ) """ # had to be select distinct???
        await self.sql.execute("SELECT user_id FROM giveaway_joins WHERE message_id = %s;", (messageid,))
        participants = await self.sql.fetchall()
        participants_count = self.sql.rowcount
        winnerscount = (
            await self.sup_db.table("giveaway_list")
            .select("winners")
            .eq("message_id", messageid)
            .execute()
        )
        await self.sql.execute("SELECT winners FROM giveaway_list WHERE message_id = %s;", (messageid,))
        winnerscount = self.sql.fetchone()[0]
        #winnerscount = winnerscount.data[0]["winners"]
        if winnerscount > participants_count:
            winnerscount = participants_count
        winners = random.sample(participants, winnerscount)
        return {
            "winners": winners,
            "winners_count": winnerscount,
            "participants": participants,
            "participants_count": participants_count,
        }


# CUSTOM CONVERTER
class Colour(discord.ext.commands.Converter):
    async def convert(self, ctx, arg: str):
        arg = arg.strip().lower()
        if arg.startswith("#"):
            arg = arg[1:]
        if not re.fullmatch("^[a-f0-9]{6}$", arg):
            raise discord.ext.commands.BadArgument("Bad hex")
        arg = int("0x" + arg, 16)
        print(arg, type(arg))
        return arg


class helper_funcs:
    def __init__(self):
        pass

    async def replace_placeholders(
        self, message, ctx, image_url=False, bot=None
    ):  # worst function ever..
        if isinstance(ctx, discord.commands.context.ApplicationContext):
            userid = ctx.user.id
            guild = ctx.user.guild
        else:  # member object
            userid = ctx.id
            guild = ctx.guild
        if bot is None:
            user = ctx.bot.get_user(
                userid
            )  # call and not use ctx.user as it doesnt have ctx.user.banner
        else:
            user = bot.get_user(userid)
        if image_url:
            if message.lower().strip() == "[user_banner]":
                message = user.banner.url if user.banner else None
            elif message.lower().strip() == "[server_icon]":
                message = guild.icon.url if guild.icon else None
            elif message.lower().strip() == "[user_avatar]":
                message = user.display_avatar.url
            return message
        suffix_num = ["th", "st", "nd", "rd"]
        suffix_num.extend(["th"] * 6)
        temp = int(str(guild.member_count)[-1])
        suffix_num = suffix_num[temp]
        placeholders = {
            "user_mention": user.mention,
            "n": "\n",
            "user": user.display_name,
            "user_id": user.id,
            "server": guild.name,
            "server_id": guild.id,
            "server_icon": guild.icon.url if guild.icon else None,
            "member_count": guild.member_count,
            "member_position": f"{guild.member_count}{suffix_num}",
            "user_avatar": user.display_avatar.url,
            "user_banner": user.banner.url if user.banner else None,
        }
        for k, v in placeholders.items():
            message = message.replace(f"[{k}]", str(v))
        return message


loop = asyncio.get_event_loop()
db = loop.run_until_complete(database.create())
# sup_db = await db.db()
funcs = helper_funcs()
