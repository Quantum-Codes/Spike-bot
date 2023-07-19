# FIX FROM LINE 42
from discord_webhook import DiscordWebhook, DiscordEmbed 
import os, json, pickle 
import googleapiclient.discovery

guild_ids = [1099306183426326589]
channelid = "UCyjy3LTL7AIV_Iwf4A9PeGw"

def yt_webhook(video=0):
  
  os.environ["OAUTHLIB_INSECURE_TRANSPORT"] = "0"
  api_service_name = "youtube"
  api_version = "v3"
  DEVELOPER_KEY = os.environ["yt_key"]

  youtube = googleapiclient.discovery.build(
      api_service_name, api_version, developerKey = DEVELOPER_KEY, static_discovery=False)

  request = youtube.channels().list(
      part="snippet,contentDetails",
      id=channelid
  )
  response = request.execute()["items"]
  request = youtube.playlistItems().list(
      part="snippet,contentDetails",
      maxResults=5,
      playlistId= response[0]["contentDetails"]["relatedPlaylists"]["uploads"]
  )

  response2 = request.execute()
  video_set = set([json.dumps(item["snippet"]) for item in response2["items"]])
  with open("webhooks/videoset.dat", "rb+") as file:
    file.seek(0)
    old_video_set = pickle.load(file)
    file.truncate(0)
    pickle.dump(video_set, file)
  new_videos = video_set - old_video_set
  print(len(new_videos))
  channel, videos = response, response2
  video = videos["items"][video]


  webhook = DiscordWebhook(url=os.environ["webhook_url"], content="@everyone New video")
  embed = DiscordEmbed(title=video["title"], description=video["description"][:150]+"...", color='03b2f8', url=f"https://youtube.com/watch?v={video['contentDetails']['videoId']}")
  embed.set_author(name=channel["snippet"]["customUrl"], url=f'https://youtube.com/{channel["snippet"]["customUrl"]}', icon_url=channel["snippet"]["thumbnails"]["default"]["url"]) 
  embed.set_image(url=video["thumbnails"]["maxres"]["url"])
  ##embed.set_thumbnail(url='https://dummyimage.com/480x300&text=thumb') 
  #embed.set_footer(text='Embed Footer Text', icon_url="https://dummyimage.com/200x200&text=footer")
  #embed.add_embed_field(name='Field 1', value='Lorem ipsum') 
  #embed.add_embed_field(name='Field 2', value='dolor sit') 
  webhook.add_embed(embed)
  """
  res = webhook.execute()
  with open("abc.json", "a") as file:
      file.write(video['contentDetails']['videoId']+"\n")
  print(res)
  print(res.json())
  """
yt_webhook()