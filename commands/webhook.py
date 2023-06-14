from discord_webhook import DiscordWebhook, DiscordEmbed 
import os, discord
import googleapiclient.discovery

guild_ids = [1099306183426326589]

def yt_webhook(repeat=False):
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
  if not repeat:
    with open("abc.json", "r") as file:
      if video['contentDetails']['videoId'] in file.read():
        return "done before"
    with open("abc.json", "a") as file:
      file.write(video['contentDetails']['videoId'])
      
  webhook = DiscordWebhook(url=os.environ["webhook_url"], content="@everyone New video")
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

class confirm_repeat(discord.ui.View):
  async def on_timeout(self):
    self.disable_all_items()
    await self.message.edit(view=self)

  @discord.ui.button(label= "Post again!", style=discord.ButtonStyle.primary, emoji=None)
  async def button_callback(self, button, interaction):
    button.disabled = True
    button.style = discord.ButtonStyle.success
    await interaction.response.edit_message(view=self)
    yt_webhook(repeat=True)
    await interaction.followup.send("done")
    
  @discord.ui.select( # the decorator that lets you specify the properties of the select menu
      placeholder = "Choose another video", # the placeholder text that will be displayed if nothing is selected
      min_values = 1, # the minimum number of values that must be selected by the users
      max_values = 1, # the maximum number of values that can be selected by the users
      options = [ # the list of options from which users can choose, a required field
          discord.SelectOption(
              label="Last video",
              description="idk"
          ),
          discord.SelectOption(
              label="2nd last video",
              description="idk"
          ),
          discord.SelectOption(
              label="3rd last video",
              description="idk"
          )
      ]
  )
  async def select_callback(self, select, interaction): # the function called when the user is done selecting options
    self.disable_all_items()
    await interaction.response.edit_message(view=self)
    await interaction.followup.send(f"Awesome! But select menu doesn't work now. use button instead")


class yt_notify_webhook(discord.Cog):
  def __init__(self, bot):
    self.bot = bot
  
  @discord.slash_command(name="notify", description ="youtube video notification", guild_ids=guild_ids)
  async def notify(self, ctx):
    if ctx.author.id in [638738610564235265,718830331356250202]:
      if yt_webhook() == "done before":
        await ctx.respond("I have already posted about the latest video.", view=confirm_repeat(timeout=30))#yt_webhook))
      else:
        await ctx.respond("done")
    else:
      await ctx.respond("who are you??")




def setup(bot):
  bot.add_cog(yt_notify_webhook(bot))