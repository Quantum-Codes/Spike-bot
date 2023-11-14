#ONLY ADDED VIDEO PARAM IN LINE 8 WEBHOOK.PY. code doesnt use it. make it use
#For replit only:
#make pycord work by making guessImports = false in .replit
#also add pkgs.ffmpeg in replit.nix for voice

import discord, os
from keep_alive import keep_alive
from components.buttons import GiveawayJoin




if "REPL_SLUG" not in os.environ: #detect replit
  import dotenv
  dotenv.load_dotenv()
  


bot = discord.Bot(intents=discord.Intents.all())
guild_ids = [1099306183426326589]#HARDCODED IN OTHER PLACES

@bot.event
async def on_ready():
  print(f"{bot.user} is ready and online!")
  bot.add_view(GiveawayJoin())

@bot.event
async def on_message(message):
  if bot.user.mentioned_in(message) and message.mentions: #message.mentions empty when everyone ping
    await message.reply("Why u pinged me? I was sleeping :(")

def welcome_embed(user):
  suffix_num = ["th","st", "nd", "rd"]
  suffix_num.extend(["th"]*6)
  temp =int(str(user.guild.member_count)[-1])
  suffix_num = suffix_num[temp]
  embed = discord.Embed(
    title = f"Welcome to Juuzou's Server {user.display_name}",
    color = discord.Colour.blurple(),
    description = f"""🎉You are the {user.guild.member_count}{suffix_num} member of Juuzou Gaming Server!🎉
----------------------------------------------
Read the <#1114076581804126228>! 
Check out <#1114076810901209088> to look for giveaways and announcements
Or go to <#1099306183979970661> to chat with other users
----------------------------------------------"""
  )
  embed.set_thumbnail(url=user.display_avatar)
  embed.set_image(url="https://media.tenor.com/4GQvhQ5ISmUAAAAC/discord-server.gif")
  return embed

@bot.event
async def on_member_join(member):
  if member.guild.id == 1099306183426326589:
    await bot.get_channel(1116003307694067772).send(f'Welcome to the server, {member.mention}! Enjoy your stay here.', embed=welcome_embed(member))

"""
@bot.listen()
async def on_interaction(interaction):
  print(interaction.data)
  print(interaction.id)
"""

@bot.event
async def on_member_update(before, after):
  if before.roles != after.roles:
    embed = discord.Embed(
        title= "Country Count",
        color= discord.Colour.blurple(),
    )
    for item in (1149669861132357693,1149670051608277002,1149670359902203925,1149670166263779379,1149669976526032896,1149670113587511387):
      role = bot.get_guild(1099306183426326589).get_role(item)
      embed.add_field(name = role.name, value = len(role.members))
    channel = bot.get_channel(1149749715840274585)
    message = await channel.fetch_message(1156230990402965616)
    await message.edit(embed=embed)

bot.load_extension("commands.general")
bot.load_extension("commands.webhook") #-- add back if needed youtube commands
bot.load_extension("commands.brawlstars")
bot.load_extension("commands.menus")
bot.load_extension("commands.rolestat")
keep_alive()
try:
  bot.run(os.environ["token"])
except discord.errors.HTTPException:
  os.system("kill 1")