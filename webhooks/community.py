from discord_webhook import DiscordWebhook, DiscordEmbed 
import os, requests 

data = requests.get("https://yt.lemnoslife.com/channels?part=community&id=UCyjy3LTL7AIV_Iwf4A9PeGw")
print(data)
if data.status_code == 200:
  data = data.json()
  print(data)
else:
  print(vars(data))
  print("------_-_-_-_-_-_-_-_-_-_-_-_-_-_")
  print(dir(data))
  print(100/0) #for error


post = data["items"][0]
postdata = post["community"]

webhook = DiscordWebhook(url=os.environ["community_webhook_url"], content="<yt ping>")
embed = DiscordEmbed(title="Community Post", description= postdata[0]["contentText"][0]["text"][:150], color='03b2f8', url=f'https://www.youtube.com/post/{postdata[0]["id"]}')
#embed.set_author(name="@Juuzou_gaming", url=f'https://youtube.com/', icon_url="") 
if postdata.get("images"):
  embed.set_image(url = postdata["images"][0]["thumbnails"][-1]["url"])
##embed.set_thumbnail(url='https://dummyimage.com/480x300&text=thumb') 
#embed.set_footer(text='Embed Footer Text', icon_url="https://dummyimage.com/200x200&text=footer")
#embed.add_embed_field(name='Field 1', value='Lorem ipsum') 
#embed.add_embed_field(name='Field 2', value='dolor sit') 
webhook.add_embed(embed)
res = webhook.execute()
print(res)
print(res.json())
