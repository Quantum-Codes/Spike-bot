import discord, requests, os, asyncio
from db import db
from main import guild_ids
from discord.commands import SlashCommandGroup


class bs_api:
  def __init__(self) -> None:
    self.headers = {"Authorization": f"Bearer {os.environ['bs_token']}"}
    self.bsapi_url = "https://bsproxy.royaleapi.dev/v1"

  def get_player(self, tag):
    data = requests.get(f"{self.bsapi_url}/players/{tag}", headers=self.headers)
    return data
  
  def get_battlelog(self, tag):
    data = requests.get(f"{self.bsapi_url}/players/{tag}/battlelog", headers=self.headers)
    return data
  
  def get_club(self, tag):
    data = requests.get(f"{self.bsapi_url}/clubs/{tag}", headers=self.headers)
    return data


def fix_playertag(player_tag):
  if not player_tag.startswith("#") and not player_tag.startswith("%23"):
    player_tag = "#"+player_tag
  player_tag = player_tag.replace("#", "%23").strip().upper()
  return player_tag 

def get_battledata(player_tag, player=None):
  api = bs_api()
  player_tag = fix_playertag(player_tag)
  data = api.get_battlelog(player_tag)
  if data.status_code == 200: 
    data = data.json()
    if not player: # if we already have player object, then no need to request again
      player = api.get_player(player_tag).json()
    raw_stats = {"victory": 0, "defeat": 0, "draw": 0, "starplayer": 0}
   # print(data['items'][0]['battle'].keys())
    for item in data["items"]:
    #  print(item)
      battleresult = item["battle"].get("result")
      if battleresult is None:#showdown
        battleresult = item["battle"].get("rank")

        if battleresult is None:
          print(item)
          continue
        battleresult = "victory" if battleresult <= (2 if item["battle"]["mode"] == "duoShowdown" else 4) else "defeat" #since lonestar, takedown also has 4 winners. so on else clause
      if raw_stats.get(battleresult) is not None:
        raw_stats[battleresult] += 1
        if battleresult == "victory":
          starplayer = item["battle"].get("starPlayer")
          if starplayer is None:
            if "Showdown" in  item["battle"]["mode"]:
              if item["battle"]["rank"] <= (1 if "duo" in item["battle"]["mode"] else 2):
                raw_stats["starplayer"] += 1
          else:
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

def TagNotFoundEmbed(mode="save", player_tag=""):
  embed = discord.Embed(colour = discord.Colour.magenta())
  if mode == "save":
    embed.add_field(name= "Tag not saved", value="Save your tag first by using `/save` command with the `player_tag` parameter")
  elif mode == "404":
    embed.add_field(name="User not found", value = f"No such player exists with tag {player_tag}. Check the tag again.")
  embed.set_image(url="https://i.imgur.com/PZBZ9a6.png")
  return embed

def embed_player(data, battle_data):
  print(data, battle_data, sep="\n")
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
  
  if battle_data is not None:
    embed.add_field(name="Recent Win rate", value=str(battle_data["victory_rate"])+"%")
    embed.add_field(name = "Recent starplayer rate", value=str(battle_data["starplayer_rate"])+"%", inline=True)
    embed.add_field(name = "Recent loss rate", value=str(battle_data["defeat_rate"])+"%", inline=True) #replace this if space needed 
  else:
    embed.add_field(name="Recent Win rate", value="Error")
    embed.add_field(name = "Recent starplayer rate", value="Error")
    embed.add_field(name = "Recent loss rate", value="Error")

  embed.add_field(name="Champtionship Challenge", value="Qualified" if data["isQualifiedFromChampionshipChallenge"] else "Not Qualified")
  
  if data["club"].get("name") is not None: # check if joined club
    embed.add_field(name="Club name", value=data['club']['name'], inline=True)
  else:
    embed.add_field(name="Club name", value="No club joined", inline=True)

  embed.set_thumbnail(url=f"https://cdn.brawlify.com/profile/{data['icon']['id']}.png")
  return embed

def embed_club(data):
  embed = discord.Embed(
        title=f"{data['name']}",
        color= discord.Color.brand_green(),
        description = data["description"]
 )
  embed.add_field(name="Trophies", value=data['trophies'])
  embed.add_field(name="Type", value=data['type'], inline=True)
  embed.add_field(name="Required Trophies", value=data['requiredTrophies'], inline=True)
  
  roles = {"senior":0, "member":0, "vicePresident":0}
  president = None
  for item in data["members"]:
    if item["role"] == "president":
      president = item["name"]
      continue
    roles[item["role"]] += 1
  
  embed.add_field(name="President", value=president)
  embed.add_field(name="Average Trophies", value= round(data['trophies']/len(data["members"]), 2) , inline=True)
  embed.add_field(name="Something", value="aaaa", inline=True)

  embed.add_field(name="Vice Presidents", value=roles["vicePresident"])
  embed.add_field(name="Seniors", value=roles["senior"], inline=True)
  embed.add_field(name="Members", value=roles["member"], inline=True)

  embed.set_thumbnail(url=f"https://cdn.brawlify.com/club/{data['badgeId']}.png")
  return embed

class brawl(discord.Cog):
  def __init__(self, bot):
    self.bot = bot

  tagcommands = SlashCommandGroup("tag", "Handle playertags")
  
  @discord.slash_command(name="playerstats", description ="GET a player's stats")
  async def playerstats(self, ctx, player_tag: str = ""):
    api = bs_api()
    await ctx.defer()
    if not player_tag:
      data = db.get_player_tag(ctx.author.id)
      if data is None:
        await ctx.respond(embed = TagNotFoundEmbed(mode = "save"))
        return 
      player_tag = data
    player_tag = fix_playertag(player_tag)
    data = api.get_player(player_tag)
    if data.status_code == 200:
      data = data.json()
      battle_data = get_battledata(player_tag, data)
      if type(battle_data) is int:
        battle_data = None
      else:
        battle_data = battle_data[1]
      await ctx.followup.send(embed=embed_player(data, battle_data))
    elif data.status_code == 404:
        if data.json().get("reason"):
          if data.json()["reason"] == "notFound":
            await ctx.followup.send("No such player exists")
    else:
      await ctx.followup.send("error")

  
  @discord.slash_command(name="clubstats", description="GET a club's stats")
  async def clubstats(self, ctx, club_tag: str = None):
    api = bs_api()
    await ctx.defer()
    if club_tag is None:
      # get player's club here
      data = db.get_player_tag(ctx.author.id)
      if data is None:
        await ctx.respond(embed=TagNotFoundEmbed(mode="save"))
        return
      player_tag = data
      playerdata = api.get_player(player_tag).json() # assumed if tag saved in db then its valid
      club_tag = playerdata["club"].get("tag")
      if club_tag is None:
        await ctx.respond("You are not part of a club... Use the `club_tag` parameter to see stats of a specific club.")
        return
    club_tag = fix_playertag(club_tag)
    data = api.get_club(club_tag)
    if data.status_code == 200:
      data = data.json()
      print(data)
      await ctx.followup.send(embed=embed_club(data))
    elif data.status_code == 404:
      if data.json().get("reason"):
        if data.json()["reason"] == "notFound":
          await ctx.followup.send("No such club exists")
    else:
      await ctx.followup.send("error")


  @discord.slash_command(name="battlestats", description ="GET a player's battle stats") 
  async def battlestats(self, ctx, player_tag: str = ""):
    await ctx.defer()
    if not player_tag:
      data = db.get_player_tag(ctx.author.id)
      if data is None:
        await ctx.respond(embed = TagNotFoundEmbed(mode = "save"))
        return
      player_tag = data
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
    elif data_raw == 404: # also 404 with modded accs
      await ctx.followup.send("No such player exists OR this player hasn't played any battles...")
    else:
      await ctx.followup.send("error")


  @tagcommands.command(name="save", description ="Save your player tag")
  async def save_tag(self, ctx, player_tag: str):
    embed = discord.Embed(colour = discord.Colour.yellow())
    api = bs_api
    player_tag = fix_playertag(player_tag)
    #currently no verification system on tags. so duplicate checking is waste.
    #sql.execute("SELECT user_id FROM spikebot_users WHERE player_tag = %s;") #duplicate tag checker. 
    #if sql.rowcount != 0:
    #  await ctx.respond("Duplicate")
    with ctx.channel.typing():
      data = api.get_player(player_tag)
    if data.status_code == 200:
      data = data.json()
      embed.add_field(name = "Confirmation:", value= f"Are you {data['name']}? React with 👍 or 👎.\n You have 2mins to do so.")
      bot_msg = await ctx.respond(embed = embed)
      def check(reaction, user):
        return user==ctx.author and str(reaction.emoji) in ("👍","👎")
      try:
        m = await bot_msg.original_response()
        await m.add_reaction("👍")
        await m.add_reaction("👎")
        embed.fields = [] #clear for future usage 
        reaction, user = await self.bot.wait_for('reaction_add', timeout=120.0, check=check)
      except asyncio.TimeoutError:
        embed.colour = discord.colour.red()
        embed.fields = [] #just in case since in except loop
        embed.add_field(name = "Timeout", value = "you took too long.. try using command again...")
        await ctx.send(embed=embed)
        return 
    elif data.status_code == 404:
      await ctx.respond(embed = TagNotFoundEmbed(mode="404", player_tag=player_tag))
      return 
    else:
      await ctx.respond(f"error {data.status_code}")
      return 

    if str(reaction.emoji)=="👎":
      embed.add_field(name = "Cancelled.", value = "")
      embed.colour = discord.Colour.red()
      await ctx.respond(embed = embed)
      return 

    db.add_user(ctx.author.id, player_tag)

    embed.colour = discord.Colour.green()
    embed.add_field(name = "Saved tag:", value= player_tag.replace('%23', '#'))
    embed.set_footer(text= "To check your tag, use `/tag show`")
    await ctx.respond(embed = embed)

  @tagcommands.command(name="remove", description ="Delete your player tag")
  async def delete_tag(self, ctx):
    player_tag = db.get_player_tag(ctx.author.id)
    if not player_tag:
      await ctx.respond("You haven't saved a tag yet. If you want to save your tag instead,  use `/tag save` command.")
      return
    db.update_tag(ctx.author.id, None)
    await ctx.respond("Removed tag successfully.\n To save your tag again, use `/tag save` command.")
  
  @tagcommands.command(name="show", description ="Check your player tag")
  async def show_tag(self, ctx): #, user: discord.User = None):
    embed = discord.Embed(colour = discord.Colour.yellow())
    data = db.get_player_tag(ctx.author.id)
    """
    if user:
        if ctx.author.get_role(1208026724399321120): # tournament manager role ID at juuzou server 
            data = db.get_player_tag(user.id)
        else:
            await ctx.respond("Don't use this option", ephemeral=True)
            return 
    """
    if not data:
      await ctx.respond(embed=TagNotFoundEmbed(mode = "save"))
      return
    else:
      embed.colour = discord.Colour.green()
      embed.add_field(name= "Your tag:", value = data.replace('%23', '#'))
      embed.set_footer(text= "If the tag is not yours, either replace it with `/tag save` Or completely remove it by using `/tag remove` command. ")
      await ctx.respond(embed = embed)
      return
  
        
def setup(bot):
  bot.add_cog(brawl(bot))
