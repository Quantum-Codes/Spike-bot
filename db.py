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
    return self.sql.fetchone()