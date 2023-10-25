import mysql.connector, os

db = mysql.connector.connect( 
  host = os.environ["db_host"],
  user = os.environ["db_user"],
  password = os.environ["db_pass"],
  database = os.environ["db_name"], 
  autocommit = True #no way I'm committing after a read
)