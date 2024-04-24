#ONLY ADDED VIDEO PARAM IN LINE 8 WEBHOOK.PY. code doesnt use it. make it use
#For replit only:
#make pycord work by making guessImports = false in .replit
#also add pkgs.ffmpeg in replit.nix for voice
#https://docs.pycord.dev/en/stable/ext/commands/api.html#checks

# ADD funcs.replace_placeholders IN WELCOME EMBED MAKER MAIN.PY

import discord, os, time
from keep_alive import keep_alive
from components.buttons import GiveawayJoin
import dotenv
from db import db, funcs

dotenv.load_dotenv()

bot = discord.Bot(intents=discord.Intents.all())
guild_ids = [1017417232952852550, 1099306183426326589] # HARDCODED IN OTHER PLACES

@bot.event
async def on_ready():
  print(f"{bot.user} is ready and online!")
  bot.add_view(GiveawayJoin())

@bot.event
async def on_message(message):
  if bot.user.mentioned_in(message) and bot.user in message.mentions: #message.mentions empty when everyone ping
    await message.reply("Why u pinged me? I was sleeping :(")

def welcome_embed(user, settings):
  suffix_num = ["th","st", "nd", "rd"]
  suffix_num.extend(["th"]*6)
  temp =int(str(user.guild.member_count)[-1])
  suffix_num = suffix_num[temp]
  embed = discord.Embed(
    title = funcs.replace_placeholders(settings["title"], user, bot=bot),
    color = discord.Colour(settings["colour"]),
    description = funcs.replace_placeholders(settings["message"], user, bot=bot)
  )
  embed.set_thumbnail(url=funcs.replace_placeholders(settings["thumb_url"], user, bot=bot, image_url=True))
  embed.set_image(url=funcs.replace_placeholders(settings["image_url"], user, bot=bot, image_url=True))
  return embed

async def autokick(member):
  if time.time() - member.created_at.timestamp() < 7*24*3600:
    dms = await member.create_dm()
    try:
      await dms.send(f"You are autokicked from **{member.guild.name}** due to being a new account...\nJoin back when your account is __atleast 1 week old__.")
    except discord.errors.Forbidden:
      print(f"Failed to message {member.name} {member.id}")

    await member.kick(reason = "new account") #message before kick so member share server with bot

@bot.event
async def on_member_join(member):
  settings = db.get_server_settings(member.guild.id, "welcomer")
  if member.guild.id == 949272833979219988: #autokick first
    await autokick(member)
  elif settings: #if autokick, dont welcome. so elif clause
    welcomechannel = bot.get_channel(settings["channel"])
    await welcomechannel.send(f'Welcome to the server, {member.mention if settings["ping"] else None}!', embed=welcome_embed(member, settings))

"""
@bot.listen()
async def on_interaction(interaction):
  print(interaction.data)
  print(interaction.id)
"""

"""@bot.event
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
"""

bot.load_extension("commands.general")
bot.load_extension("commands.webhook")
bot.load_extension("commands.brawlstars")
####bot.load_extension("commands.message_commands")
bot.load_extension("commands.rolestat")
t1 = keep_alive()
try:
  bot.run(os.environ["token"])
  t1.join()
except discord.errors.HTTPException:
  os.system("kill 1")