#ONLY ADDED VIDEO PARAM IN LINE 8 WEBHOOK.PY. code doesnt use it. make it use
#For replit only:
#make pycord work by making guessImports = false in .replit
#also add pkgs.ffmpeg in replit.nix for voice

import discord, os
from keep_alive import keep_alive





if "REPL_SLUG" not in os.environ: #detect replit
  import dotenv
  dotenv.load_dotenv()
  


bot = discord.Bot(intents=discord.Intents.all())
guild_ids = [1099306183426326589] #HARDCODED IN OTHER PLACES

@bot.event
async def on_ready():
  print(f"{bot.user} is ready and online!")

@bot.event
async def on_message(message):
  if bot.user.mentioned_in(message) and message.mentions: #message.mentions empty when everyone ping
    await message.reply("Why u pinged me? I was sleeping :(")

@bot.event
async def on_member_join(member):
  await bot.get_channel(1116003307694067772).send(f'Welcome to the server, {member.mention}! Enjoy your stay here.')

#bot.load_extension("commands.general")
bot.load_extension("commands.webhook")
bot.load_extension("commands.brawlstars")
#bot.load_extension("commands.menu")
keep_alive()
try:
  bot.run(os.environ["token"])
except discord.errors.HTTPException:
  os.system("kill 1")