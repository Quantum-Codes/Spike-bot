from discord_webhook import DiscordWebhook, DiscordEmbed 
from logger import getlog, writelog
import os, discord
import googleapiclient.discovery

guild_ids = [1099306183426326589]
channelid = "UCyjy3LTL7AIV_Iwf4A9PeGw"
global_videolist =[] 
#setup Google api
os.environ["OAUTHLIB_INSECURE_TRANSPORT"] = "0"
api_service_name = "youtube"
api_version = "v3"
DEVELOPER_KEY = os.environ["yt_key"]

youtube = googleapiclient.discovery.build(
    api_service_name, api_version, developerKey = DEVELOPER_KEY, static_discovery=False)


def yt_webhook(video=0, check_old = False):
  request = youtube.channels().list(
      part="snippet,contentDetails",
      id=channelid
  )
  response = request.execute()["items"][0]

  request = youtube.playlistItems().list(
      part="snippet,contentDetails",
      maxResults=3,
      playlistId= response["contentDetails"]["relatedPlaylists"]["uploads"]
  )
  response2 = request.execute()
  channel, videos = response, response2
  video = videos["items"][video]

  if check_old:
    if video['contentDetails']['videoId'] in getlog():
      writelog(f"Repeated video. Rejected. {video['contentDetails']['videoId']}")
      return "Repeated"
      
  print(video)
  webhook = DiscordWebhook(url=os.environ["webhook_url"], content="<@&1149699372209164370> New video")
  embed = DiscordEmbed(title=video["snippet"]["title"], description=video["snippet"]["description"][:150]+"...", color='03b2f8', url=f"https://youtube.com/watch?v={video['contentDetails']['videoId']}")
  embed.set_author(name=channel["snippet"]["customUrl"], url=f'https://youtube.com/{channel["snippet"]["customUrl"]}', icon_url=channel["snippet"]["thumbnails"]["default"]["url"]) 
  embed.set_image(url=video["snippet"]["thumbnails"]["high"]["url"])
  ##embed.set_thumbnail(url='https://dummyimage.com/480x300&text=thumb') 
  #embed.set_footer(text='Embed Footer Text', icon_url="https://dummyimage.com/200x200&text=footer")
  #embed.add_embed_field(name='Field 1', value='Lorem ipsum') 
  #embed.add_embed_field(name='Field 2', value='dolor sit') 
  webhook.add_embed(embed)
  res = webhook.execute()
  print(res)
  print(res.json())

class yt_notify_webhook(discord.Cog):
  def __init__(self, bot):
    self.bot = bot
  
  @discord.slash_command(name="notify", description ="youtube video notification", guild_ids=guild_ids)
  async def notify(self, ctx):
    global global_videolist
    await ctx.defer()
    if ctx.author.id in [638738610564235265,718830331356250202]:
      request = youtube.playlistItems().list(
        part="snippet,contentDetails",
        maxResults=3,
        playlistId= "UUyjy3LTL7AIV_Iwf4A9PeGw"
      )
      global_videolist = request.execute()["items"]

      async def select_callback(interaction): # the function called when the user is done selecting options
        #await interaction.delete_original_response() doesn't work
        yt_webhook([item["snippet"]["title"] for item in global_videolist].index(interaction.data["values"][0]))
        await interaction.response.send_message("Done", ephemeral = True)

      
      select_menu = discord.ui.Select( # the decorator that lets you specify the properties of the select menu
      placeholder = "Choose another video", # the placeholder text that will be displayed if nothing is selected
      min_values = 1, # the minimum number of values that must be selected by the users
      max_values = 1, # the maximum number of values that can be selected by the users
      options = [ # the list of options from which users can choose, a required field
          discord.SelectOption(
              label = global_videolist[0]["snippet"]["title"],
              description="Re-notify for last video"
          ),
          discord.SelectOption(
              label = global_videolist[1]["snippet"]["title"],
              description="Re-notify for 2nd last video"
          ),
          discord.SelectOption(
              label = global_videolist[2]["snippet"]["title"],
              description="Re-notify for 3rd last video"
          )
      ]
      )
      select_menu.callback = select_callback
      msg = await ctx.respond("Choose one (you have 2mins to do so): ", view = discord.ui.View(select_menu))
      await msg.delete(delay=120)
    else:
      await ctx.followup.send("who are you??")



def setup(bot):
  bot.add_cog(yt_notify_webhook(bot))