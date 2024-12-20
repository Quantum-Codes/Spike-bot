# https://docs.pycord.dev/en/stable/ext/commands/api.html#checks
# if getting table lock error in mysql, then prob too many connections opened. close using script in killprocess.txt
# ADD funcs.replace_placeholders IN WELCOME EMBED MAKER MAIN.PY
# poetry export --without-hashes --format=requirements.txt > requirements.txt

import discord, os, time
from keep_alive import keep_alive
from components.buttons import GiveawayJoin
import dotenv
from db import db, funcs

dotenv.load_dotenv()

bot = discord.Bot(intents=discord.Intents.all())
guild_ids = [1017417232952852550, 1099306183426326589]


@bot.event
async def on_ready():
    print(f"{bot.user} is ready and online!")
    bot.add_view(GiveawayJoin())


@bot.event
async def on_message(message):
    if (
        bot.user.mentioned_in(message) and bot.user in message.mentions
    ):  # message.mentions empty when everyone ping
        await message.reply("Why u pinged me? I was sleeping :(")


async def welcome_embed(user, settings):
    suffix_num = ["th", "st", "nd", "rd"]
    suffix_num.extend(["th"] * 6)
    temp = int(str(user.guild.member_count)[-1])
    suffix_num = suffix_num[temp]
    embed = discord.Embed(
        title=await funcs.replace_placeholders(settings["title"], user, bot=bot),
        color=discord.Colour(settings["colour"]),
        description=await funcs.replace_placeholders(settings["message"], user, bot=bot),
    )
    embed.set_thumbnail(
        url=await funcs.replace_placeholders(
            settings["thumb_url"], user, bot=bot, image_url=True
        )
    )
    embed.set_image(
        url=await funcs.replace_placeholders(
            settings["image_url"], user, bot=bot, image_url=True
        )
    )
    return embed


async def autokick(member, acc_time):
    if time.time() - member.created_at.timestamp() < acc_time:
        dms = await member.create_dm()
        try:
            await dms.send(
                f"You are autokicked from **{member.guild.name}** due to being a new account...\nJoin back when your account is __atleast {acc_time} seconds old__."
            )
        except discord.errors.Forbidden:
            print(f"Failed to message {member.name} {member.id}")

        await member.kick(
            reason="new account"
        )  # message before kick so member share server with bot
        return 1
    return 0


@bot.event
async def on_member_join(member):
    settings_welcome = await db.get_server_settings(member.guild.id, "welcomer")
    settings_autokick = await db.get_server_settings(member.guild.id, "autokick")
    kicked = 0
    if settings_autokick is not None:  # autokick first
        kicked = await autokick(member, settings_autokick["age"])
    if (
        settings_welcome is not None and kicked == 0
    ):  # if autokick, dont welcome. so elif clause
        welcomechannel = bot.get_channel(int(settings_welcome["channel"]))
        await welcomechannel.send(
            f'Welcome to the server, {member.mention if settings_welcome["ping"] else None}!',
            embed=await welcome_embed(member, settings_welcome),
        )


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
bot.load_extension("commands.events")
####bot.load_extension("commands.message_commands")
bot.load_extension("commands.rolestat")
t1 = keep_alive()
try:
    bot.run(os.environ["token"])
    t1.join()
except discord.errors.HTTPException  as e:
    print("Login error")
    print(e)
    exit(1)
