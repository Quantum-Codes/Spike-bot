import discord, json, requests 
from main import guild_ids

class brawl(discord.Cog):
  def __init__(self, bot):
    self.bot = bot
  
  @discord.slash_command(name="playerstats", description ="GET a player's stats", guild_ids=guild_ids)
  async def playerstats(self, ctx, player_id: str):
    if player_id.startswith("#"):
      player_id = player_id[1:]
    data = requests.get(f"https://cr.is-a.dev/{player_id}")
    if data.status_code == 200:
      data = data.json()
      await ctx.respond(f"STILL WIP \n```{json.dumps(data, indent=2)[:1800]}...\n```")
    else:
      await ctx.respond("error")




def setup(bot):
  bot.add_cog(brawl(bot))