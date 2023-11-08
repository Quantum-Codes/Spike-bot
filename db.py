import mysql.connector, os


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
    return self.sql.rowcount

  def join_leave_giveaway(self, messageid, userid, mode="join"):
    if mode == "leave":
      self.sql.execute("DELETE FROM spikebot_giveaway_joins WHERE messageid = %s AND userid = %s;", (messageid,  userid))
    else:
      self.sql.execute("INSERT INTO spikebot_giveaway_joins (messageid, userid) VALUES (%s, %s);", (messageid, userid))

db = database()
sql = db.cursor()