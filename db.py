import discord.ui
import os, random, json, supabase, dotenv

dotenv.load_dotenv()
class database:
  def __init__(self):
    # connects to the database
    self.sup_db = supabase.create_client(os.environ["sup_url"], os.environ["sup_key"])

  def db(self):
    return self.sup_db

  def get_server_settings(self, serverid, setting_type = None):
    if setting_type is None:
      result = self.sup_db.table("server_settings").select("type, data").eq("server_id", serverid).execute().data
      print(setting_type(result), result, setting_type(result[0]["data"]))
      data = [(item["type"], item["data"]) for item in result]
      print(data)
      return data if data else None
    data = self.sup_db.table("server_settings").select("data").eq("server_id", serverid).eq("type", setting_type).execute().data
    if data: # non empty list= True
      data = data[0]["data"] # guaranteed to be list of 1 element, so take just the 1st one
    else:
      data = None
    return data

  def save_server_settings(self, serverid, setting_type, data):
    if self.get_server_settings(serverid, setting_type) is None:
      self.sup_db.table("server_settings").insert({"server_id": serverid, "type": setting_type, "data": data}).execute()
      return
    self.sup_db.table("server_settings").update({"data": data}).eq("server_id", serverid).eq("type", setting_type).execute()

  def get_player_tag(self, discordid, check_deleted=False):
    """
    `check_deleted` is used internally to test if a player has his tag deleted (used in add_user func)
    """
    data = self.sup_db.table("users").select("player_tag").eq("user_id", discordid).execute()
    if len(data.data) == 0:
      if check_deleted:
        return None, False
      else:
        return None
    tag = data.data[0]["player_tag"]
    if check_deleted:
      return tag, bool(tag is None)
    else:
      return tag


  def update_tag(self, discordid, player_tag = None):
    self.sup_db.table("users").update({"player_tag": player_tag}).eq("user_id", discordid).execute()

  def add_user(self, discordid, player_tag = None):
    """
    Only `discordid` is required. All others are optional params. default = None
    """
    tag = self.get_player_tag(discordid, check_deleted=True)
    if type(tag[0]) is str or tag[1]:
      self.update_tag(discordid, player_tag)
      return
    self.sup_db.table("users").insert({"user_id": discordid, "player_tag": player_tag}).execute()


  def create_giveaway(self, messageid, channelid, winners):
    """
    All params required.
    `winners` = Number of winners
    `messageid` = Message id of bot-posted giveaway
    `channelid` = Channel id of giveaway message
    """
    self.sup_db.table("giveaway_list").insert({"message_id":messageid, "winners":winners, "channel_id": channelid}).execute()

  def check_joined_giveaway(self, messageid, userid):
    data = self.sup_db.table("giveaway_joins").select("*").eq("message_id", messageid).eq("user_id", userid).execute()
    return len(data.data) # tests truth value

  def check_valid_giveaway(self, messageid):
    data = self.sup_db.table("giveaway_list").select("*").eq("message_id", messageid).execute()
    return len(data.data) # tests truth value

  def join_leave_giveaway(self, messageid, userid, mode="join"):
    if mode == "leave":
      self.sup_db.table("giveaway_joins").delete().eq("message_id", messageid).eq("user_id", userid).execute()
    else:
      self.sup_db.table("giveaway_joins").insert({"message_id": messageid, "user_id": userid}).execute()

  async def cleanup_giveaway(self, ctx, messageid):
    """
    AWAIT THIS
    run after all rerolling and winner choosing done AND all prizes claimed.
    deletes all joins and giveaway data from db.
    """
    self.sup_db.table("giveaway_joins").delete().eq("message_id", messageid).execute()
    channelid = self.sup_db.table("giveaway_list").delete().eq("message_id", messageid).execute().data[0]["channel_id"]
    channel = ctx.guild.get_channel(channelid)
    message = await channel.fetch_message(messageid)
    view = discord.ui.View.from_message(message)
    view.disable_all_items()
    await message.edit(view=view)



  def end_giveaway(self, messageid):
    """
    Does not edit/delete db. Only reads to db
    Return value: dict. (keys: winners, winners_count, participants, participants_count)
    participants, winners -> list of single item tuples with discord ID (int) inside them.
    """
    participants = self.sup_db.table("giveaway_joins").select("user_id").eq("message_id", messageid).execute().data # had to be select distinct???
    print(participants)
    participants_count = len(participants)
    winnerscount = self.sup_db.table("giveaway_list").select("winners").eq("message_id", messageid).execute().data[0]["winners"]
    if winnerscount > participants_count:
      winnerscount = participants_count
    winners = random.sample(participants, winnerscount)
    return {"winners": winners, "winners_count": winnerscount, "participants": participants, "participants_count": participants_count}


class helper_funcs:
  def __init__(self):
    pass

  def replace_placeholders(self, message, user, test = False):
    suffix_num = ["th","st", "nd", "rd"]
    suffix_num.extend(["th"]*6)
    temp =int(str(user.guild.member_count)[-1])
    suffix_num = suffix_num[temp]
    placeholders = {
      "user_mention": "@testuser" if test else user.mention,
      "user": "testuser" if test else user.display_name,
      "user_id": "testuserid" if test else user.id,
      "server": user.guild.name,
      "server_id": user.guild.id,
      "member_count": user.guild.member_count,
      "member_position": f"{user.guild.member_count}{suffix_num}"
    }
    for k, v in placeholders.items():
      message = message.replace(f"[{k}]", str(v))
    return message



db = database()
sup_db = db.db()
funcs = helper_funcs()