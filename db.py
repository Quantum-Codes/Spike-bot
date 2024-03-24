import mysql.connector, os, random, json, supabase, dotenv

dotenv.load_dotenv()
class database:
  def __init__(self):
    self.db = mysql.connector.connect( 
      host = os.environ["db_host"],
      user = os.environ["db_user"],
      password = os.environ["db_pass"],
      database = os.environ["db_name"], 
      autocommit = True #no way I'm committing after every read
    )
    self.sql = self.db.cursor()
    self.sup_db = supabase.create_client(os.environ["sup_url"], os.environ["sup_key"])


  def cursor(self):
    return self.sql

  def get_server_settings(self, serverid, type = None):
    if not type:
      self.sql.execute("SELECT type, data FROM spikebot_server_settings WHERE serverid = %s;", (serverid,))
      result = self.sql.fetchall()
      data = [(item[0], json.loads(item[1])) for item in result]
      return data if data else None
    self.sql.execute("SELECT data FROM spikebot_server_settings WHERE serverid = %s AND type = %s;", (serverid, type))
    data = self.sql.fetchone()
    if data:
      data = json.loads(data[0])
    else:
      data = None
    return data

  def save_server_settings(self, serverid, type, data):
    if self.get_server_settings(serverid, type) is None:
      self.sql.execute("INSERT INTO spikebot_server_settings (serverid, type, data) VALUES (%s, %s, %s);", (serverid, type, json.dumps(data)))
      return
    self.sql.execute("UPDATE spikebot_server_settings SET data = %s WHERE serverid = %s AND type = %s;",(json.dumps(data), serverid, type))
    
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


  def create_giveaway(self, messageid, winners):
    """
    All params required.
    `winners` = Number of winners
    `messageid`  = Message id of bot-posted giveaway 
    """
    self.sup_db.table("giveaway_list").insert({"message_id":messageid, "winners":winners}).execute()

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

  def cleanup_giveaway(self, messageid): 
    """
    run after all rerolling and winner choosing done AND all prizes claimed.
    deletes all joins and giveaway data from db.
    """
    self.sup_db.table("giveaway_joins").delete().eq("message_id", messageid).execute()
    self.sup_db.table("giveaway_list").delete().eq("message_id", messageid).execute()


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
sql = db.cursor()
funcs = helper_funcs()