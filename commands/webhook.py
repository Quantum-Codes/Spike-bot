from discord_webhook import DiscordWebhook, DiscordEmbed 
import os, json, discord
import googleapiclient.discovery

guild_ids = [1099306183426326589]

def yt_webhook():
  os.environ["OAUTHLIB_INSECURE_TRANSPORT"] = "0"
  api_service_name = "youtube"
  api_version = "v3"
  DEVELOPER_KEY = os.environ["yt_key"]

  youtube = googleapiclient.discovery.build(
      api_service_name, api_version, developerKey = DEVELOPER_KEY, static_discovery=False)

  request = youtube.channels().list(
      part="snippet,contentDetails",
      id="UCyjy3LTL7AIV_Iwf4A9PeGw"
  )
  response = request.execute()["items"][0]

  request = youtube.playlistItems().list(
      part="snippet,contentDetails",
      maxResults=2,
      playlistId= response["contentDetails"]["relatedPlaylists"]["uploads"]
  )
  response2 = request.execute()
  channel, videos = response, response2
  video = videos["items"][0]
  with open("abc.json", "r") as file:
    if video in json.load(file):
      return 
  with open("abc.json", "a") as file:
    file.write(json.dumps(video, indent=2))
  webhook = DiscordWebhook(url=os.environ["webhook_url"], content="@everyone New video")#, allowed_mentions=["everyone"])
  embed = DiscordEmbed(title=video["snippet"]["title"], description=video["snippet"]["description"][:150]+"...", color='03b2f8', url=f"https://youtube.com/watch?v={video['contentDetails']['videoId']}")
  embed.set_author(name=channel["snippet"]["customUrl"], url=f'https://youtube.com/{channel["snippet"]["customUrl"]}', icon_url=channel["snippet"]["thumbnails"]["default"]["url"]) 
  embed.set_image(url=video["snippet"]["thumbnails"]["maxres"]["url"])
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
    if ctx.author.id in [638738610564235265,718830331356250202]:
      yt_webhook()
      await ctx.respond("done")
    else:
      await ctx.respond("who are you??")




def setup(bot):
  bot.add_cog(yt_notify_webhook(bot))