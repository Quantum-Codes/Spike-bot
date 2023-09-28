import discord, json, requests, os
from main import guild_ids

headers = {
  "Authorization": f"Bearer {os.environ['bs_token']}"
}

def get_battledata(player_tag, player=None):
  if not player_tag.startswith("#") and not player_tag.startswith("%23"):
    player_tag = "#"+player_tag
  player_tag = player_tag.replace("#", "%23").strip().upper()
  print (player_tag)
  data = requests.get(f"https://bsproxy.royaleapi.dev/v1/players/{player_tag}/battlelog", headers=headers)
  if data.status_code == 200: 
    data = data.json()
    if not player:
      player = requests.get(f"https://bsproxy.royaleapi.dev/v1/players/{player_tag}", headers=headers).json()
    raw_stats = {"victory": 0, "defeat": 0, "draw": 0, "starplayer": 0}
   # print(data['items'][0]['battle'].keys())
    for item in data["items"]:
      battleresult = item["battle"]["result"]
      if raw_stats.get(battleresult) is not None:
        raw_stats[battleresult] += 1
        if battleresult == "victory":
          if item['battle']['starPlayer']['tag'].upper() == player['tag'].upper():
            raw_stats["starplayer"] += 1
      else:
        raw_stats.setdefault(battleresult, 1)
    stats = {}
    print(raw_stats)
    raw_stats2 = raw_stats.copy()
    raw_stats2.pop("starplayer")
    total_matches = sum(raw_stats2.values())
    for k, v in raw_stats.items():
      if k == "starplayer":
        stats[k+"_rate"] = int(round(v / raw_stats["victory"], 4)*10000)/100 #round doesn't do its job properly 
      else:
        stats[k+"_rate"] = int(round(v / total_matches, 4)*10000)/100

    return (player, stats)
         
  elif data.status_code == 404:
      if data.json().get("reason"):
        if data.json()["reason"] == "notFound":
           return 404
  else:
    return 500


def embed_player(data, battle_data):
  embed = discord.Embed(
        title=f"{data['name']}",
        color= int(data['nameColor'][4:], base=16),
 )
  embed.add_field(name="Trophies", value=data['trophies'])
  embed.add_field(name="Highest Trophies", value=data['highestTrophies'], inline=True)
  embed.add_field(name="Exp Level", value=data['expLevel'], inline=True)

  embed.add_field(name="3v3 wins", value=data['3vs3Victories'])
  embed.add_field(name="solo wins", value=data['soloVictories'], inline=True)
  embed.add_field(name="duo wins", value=data['duoVictories'],  inline=True)

  embed.add_field(name="Recent Win rate", value=str(battle_data["victory_rate"])+"%")
  embed.add_field(name = "Recent starplayer rate", value=str(battle_data["starplayer_rate"])+"%", inline=True)
  embed.add_field(name = "Recent loss rate", value=str(battle_data["defeat_rate"])+"%", inline=True) #replace this if space needed later
  
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
    if not player_tag.startswith("#") and not player_tag.startswith("%23"):
      player_tag = "#"+player_tag
    player_tag = player_tag.replace("#", "%23").strip().upper()
    
    data = requests.get(f"https://bsproxy.royaleapi.dev/v1/players/{player_tag}", headers=headers)
    if data.status_code == 200:
      data = data.json()
      print(player_tag)
      battle_data = get_battledata(player_tag, data)[1]
      await ctx.followup.send(embed=embed_player(data, battle_data))
    elif data.status_code == 404:
        if data.json().get("reason"):
          if data.json()["reason"] == "notFound":
            await ctx.followup.send("No such player exists")
    else:
      await ctx.followup.send("error")


  @discord.slash_command(name="battlestats", description ="GET a player's battle stats") 
  async def battlestats(self, ctx, player_tag: str):
    await ctx.defer()
    data_raw = get_battledata(player_tag)
    if type(data_raw) is not int: 
      player, data = data_raw
      message = f"# {player['name']}'s stats\n"
      message += "\n".join([f"**{I[0]}**: {I[1]}" for I in data.items()])
      embed = discord.Embed(
        title=f"{player['name']}'s stats",
        color=discord.Colour.dark_gold()
      )
      for k,v in data.items():
        embed.add_field(name=k, value=str(v)+"%")
      embed.set_footer(text="Data from last 25 matches")
  
      await ctx.followup.send(embed=embed)
    elif data_raw == 404:
      await ctx.followup.send("No such player exists")
    else:
      await ctx.followup.send("error")



def setup(bot):
  bot.add_cog(brawl(bot))