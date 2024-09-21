import mysql.connector, dotenv, os, supabase, json

dotenv.load_dotenv()

mydb = mysql.connector.connect(
            user=os.environ["db_user"],
            password=os.environ["db_pass"],
            host=os.environ["db_host"],
            port=3306,
            db=os.environ["db_name"],
        )
sudb = supabase.create_client(os.environ["sup_url"], os.environ["sup_key"])
mysql = mydb.cursor()

users = sudb.table("users").select("*").execute().data
print("User table:", len(users), "records")
for item in users:
    mysql.execute("INSERT INTO users VALUES (%s, %s);", (str(item["user_id"]), item["player_tag"]))

server_settings = sudb.table("server_settings").select("*").execute().data
print("Server settings table:", len(server_settings), "records")
for item in server_settings:
    mysql.execute("INSERT INTO server_settings (server_id, type, data) VALUES (%s, %s, %s);", (str(item["server_id"]), str(item["type"]), json.dumps(item["data"])))
    
    
mydb.commit()