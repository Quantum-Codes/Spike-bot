import discord, json, requests, os
from main import guild_ids

headers = {
  "Authorization": f"Bearer {os.environ['bs_token']}"
}

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
  
  @discord.slash_command(name="playerstats", description ="GET a player's stats", guild_ids=guild_ids)
  async def playerstats(self, ctx, player_tag: str):
    await ctx.defer()
    if not player_tag.startswith("#"):
      player_tag = "#"+player_tag
    player_tag = player_tag.replace("#", "%23")
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



def setup(bot):
  bot.add_cog(brawl(bot))