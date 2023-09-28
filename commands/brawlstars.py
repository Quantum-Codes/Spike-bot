import discord, json, requests, os
from main import guild_ids

headers = {
  "Authorization": f"Bearer {os.environ['bs_token']}"
}

def get_battledata(player_tag):
  if not player_tag.startswith("#"):
    player_tag = "#"+player_tag
  player_tag = player_tag.replace("#", "%23").strip().upper()
  
  data = requests.get(f"https://bsproxy.royaleapi.dev/v1/players/{player_tag}/battlelog", headers=headers)
  if data.status_code == 200:  #CHANGE FROM HERE
    data = data.json()
    raw_stats = {"victory": 0, "defeat": 0, "draw": 0}
    #print(data['items'][0]['battle'].keys())
    player = data["items"][0]['battle']["teams"][0][0]
    for item in data["items"]:
      battleresult = item["battle"]["result"]
      if raw_stats.get(battleresult):
        raw_stats[battleresult] += 1
        print(battleresult )
      else:
        raw_stats.setdefault(battleresult, 1)
        print(battleresult, "new")
    stats = {}
    print(raw_stats )
    for k, v in raw_stats.items():
      stats[k+"_rate"] = round(v / sum(raw_stats.values()), 2)

    return (player, stats)
         
  elif data.status_code == 404:
      if data.json().get("reason"):
        if data.json()["reason"] == "notFound":
           return 404
  else:
    return 500


def embed_player(data):
  embed = discord.Embed(
        title=f"{data['name']}'s stats",
        color= int(data['nameColor'][4:], base=16),
 )
  embed.add_field(name="Trophies", value=data['trophies'])
  embed.add_field(name="Highest Trophies", value=data['highestTrophies'], inline=True)
  embed.add_field(name="Exp Level", value=data['expLevel'], inline=True)

  embed.add_field(name="3v3 wins", value=data['3vs3Victories'])
  embed.add_field(name="solo wins", value=data['soloVictories'], inline=True)
  embed.add_field(name="duo wins", value=data['duoVictories'],  inline=True)
  
  embed.add_field(name="Club tag", value=data['club']['tag'])
  embed.add_field(name="Club name", value=data['club']['name'], inline=True)

  embed.set_thumbnail(url=f"https://cdn.brawlify.com/profile/{data['icon']['id']}.png")
  return embed


class brawl(discord.Cog):
  def __init__(self, bot):
    self.bot = bot
  
  @discord.slash_command(name="playerstats", description ="GET a player's stats")
  async def playerstats(self, ctx, player_tag: str):
    await ctx.defer()
    if not player_tag.startswith("#"):
      player_tag = "#"+player_tag
    player_tag = player_tag.replace("#", "%23").strip().upper()
    
    data = requests.get(f"https://bsproxy.royaleapi.dev/v1/players/{player_tag}", headers=headers)
    if data.status_code == 200:
      data = data.json()
      await ctx.followup.send(embed=embed_player(data))
    elif data.status_code == 404:
        if data.json().get("reason"):
          if data.json()["reason"] == "notFound":
            await ctx.followup.send("No such player exists")
    else:
      await ctx.followup.send("error")


  @discord.slash_command(name="battlestats", description ="GET a player's battle stats") #DOING
  async def battlestats(self, ctx, player_tag: str):
    await ctx.defer()
    data_raw = get_battledata(player_tag)
    if type(data_raw) is not int: 
      player, data = data_raw
      message = f"# {player['name']}'s stats\n"
      message += "\n".join([f"**{I[0]}**: {I[1]}" for I in data.items()])
      await ctx.followup.send(message)
    elif data_raw == 404:
      await ctx.followup.send("No such player exists")
    else:
      await ctx.followup.send("error")



def setup(bot):
  bot.add_cog(brawl(bot))