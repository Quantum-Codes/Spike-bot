from discord_webhook import DiscordWebhook, DiscordEmbed 
import os, requests, json, string

data = requests.get("https://yt.lemnoslife.com/channels?part=community&id=UCyjy3LTL7AIV_Iwf4A9PeGw")
if data.status_code == 200:
  data = data.json()
  print(json.dumps(data, indent = 2))
else:
  print(vars(data))
  print("------_-_-_-_-_-_-_-_-_-_-_-_-_-_")
  print(dir(data))
  assert 1+1 == 5 #for error
  
print((("*"*50)+"\n")*3)
post = data["items"][0]
postdata = post["community"][0]
print(json.dumps(postdata, indent = 2))
print((("*"*50)+"\n")*3)

options = ""
image = ""
if postdata.get("poll"):
  options= "\n"
  for idx, option in zip(string.ascii_uppercase, postdata["poll"]["choices"]):
    options += f"{idx}. {option['text']}\n"
    if option.get("images"):
      image = option["images"][0]["thumbnails"][-1]["url"]
webhook = DiscordWebhook(url=os.environ["community_webhook_url"], content="<yt ping>")
embed = DiscordEmbed(title=f"Community {'Poll' if options else 'Post'}", description= postdata["contentText"][0]["text"][:150] + options, color='03b2f8', url=f'https://www.youtube.com/post/{postdata["id"]}')
#embed.set_author(name="@Juuzou_gaming", url=f'https://youtube.com/', icon_url="") 

if postdata.get("images"):
  image = postdata["images"][0]["thumbnails"][-1]["url"]
embed.set_image(url = image)
##embed.set_thumbnail(url='https://dummyimage.com/480x300&text=thumb') 
#embed.set_footer(text='Embed Footer Text', icon_url="https://dummyimage.com/200x200&text=footer")
#embed.add_embed_field(name='Field 1', value='Lorem ipsum') 
#embed.add_embed_field(name='Field 2', value='dolor sit') 
webhook.add_embed(embed)
res = webhook.execute()
print(res)
print(res.json())
