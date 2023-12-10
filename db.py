import mysql.connector, os, random, json


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
    
  def get_player_tag(self, discordid):
    self.sql.execute("SELECT player_tag FROM spikebot_users WHERE user_id = %s;", (discordid,))
    tag = self.sql.fetchone()
    if tag is None:
      return None
    return tag[0]

  def update_tag(self, discordid, player_tag = None):
    self.sql.execute("UPDATE spikebot_users SET player_tag = %s WHERE user_id = %s;", (player_tag, discordid))

  def add_user(self, discordid, player_tag = None):
    """
    Only `discordid` is required. All others are optional params. default = None
    """
    self.sql.execute("SELECT player_tag FROM spikebot_users WHERE user_id = %s;", (discordid,))
    tag = self.sql.fetchone()
    print(tag, type(tag))
    if type(tag) is tuple:
      self.update_tag(discordid, player_tag)
      return
    self.sql.execute("INSERT INTO spikebot_users (user_id, player_tag) VALUES (%s, %s);", (discordid, player_tag))


  def create_giveaway(self, messageid, winners):
    """
    All params required.
    `winners` = Number of winners
    `messageid`  = Message id of bot-posted giveaway 
    """
    self.sql.execute("INSERT INTO spikebot_giveaway_list (messageid, winners) VALUES (%s, %s);", (messageid, winners))

  def check_joined_giveaway(self, messageid, userid):
    self.sql.execute("SELECT * FROM spikebot_giveaway_joins WHERE messageid = %s AND userid = %s;", (messageid, userid))
    self.sql.fetchall()
    return self.sql.rowcount # tests truth value 

  def check_valid_giveaway(self, messageid):
    self.sql.execute("SELECT * FROM spikebot_giveaway_list WHERE messageid = %s;", (messageid,))
    return len(self.sql.fetchall()) # tests truth value 

  def join_leave_giveaway(self, messageid, userid, mode="join"):
    if mode == "leave":
      self.sql.execute("DELETE FROM spikebot_giveaway_joins WHERE messageid = %s AND userid = %s;", (messageid,  userid))
    else:
      self.sql.execute("INSERT INTO spikebot_giveaway_joins (messageid, userid) VALUES (%s, %s);", (messageid, userid))

  def cleanup_giveaway(self, messageid): 
    """
    run after all rerolling and winner choosing done AND all prizes claimed.
    deletes all joins and giveaway data from db.
    """
    self.sql.execute("DELETE FROM spikebot_giveaway_joins WHERE messageid = %s;", (messageid,))
    self.sql.execute("DELETE FROM spikebot_giveaway_list WHERE messageid = %s;", (messageid,))

  def end_giveaway(self, messageid):
    """
    Does not edit/delete db. Only reads to db
    Return value: dict. (keys: winners, winners_count, participants, participants_count)
    participants, winners -> list of single item tuples with discord ID (int) inside them.
    """
    self.sql.execute("SELECT DISTINCT userid FROM spikebot_giveaway_joins WHERE messageid = %s;", (messageid,))
    participants = self.sql.fetchall()
    participants_count = self.sql.rowcount
    self.sql.execute("SELECT winners FROM spikebot_giveaway_list WHERE messageid = %s;", (messageid,))
    winnerscount = self.sql.fetchone()[0]
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