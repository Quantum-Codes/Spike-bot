from discord_webhook import DiscordWebhook, DiscordEmbed 
import os, json

# -*- coding: utf-8 -*-

# Sample Python code for youtube.channels.list
# See instructions for running these code samples locally:
# https://developers.google.com/explorer-help/code-samples#python

import googleapiclient.discovery

def main():
    # Disable OAuthlib's HTTPS verification when running locally.
    # *DO NOT* leave this option enabled in production.
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

    #print(response)
    request = youtube.playlistItems().list(
        part="snippet,contentDetails",
        maxResults=10,
        playlistId= response["contentDetails"]["relatedPlaylists"]["uploads"]
    )
    response2 = request.execute()
    return response, response2
   
channel, videos = main()
with open("abc.json", "w") as file:
  json.dump(videos, file, indent=2)
#print(channel)


video = videos["items"][0]


webhook = DiscordWebhook(url=os.environ["webhook_url"])

embed = DiscordEmbed(title=video["snippet"]["title"], description=video["snippet"]["description"], color='03b2f8', url=f"https://youtube.com/watch?v={video['contentDetails']['videoId']}")
embed.set_author(name=channel["snippet"]["customUrl"], url=f'https://youtube.com/{channel["snippet"]["customUrl"]}', icon_url=channel["snippet"]["thumbnails"]["default"]["url"]) 
embed.set_image(url=video["snippet"]["thumbnails"]["maxres"]["url"])
##embed.set_thumbnail(url='https://dummyimage.com/480x300&text=thumb') 
#embed.set_footer(text='Embed Footer Text', icon_url="https://dummyimage.com/200x200&text=footer")
#embed.add_embed_field(name='Field 1', value='Lorem ipsum') 
#embed.add_embed_field(name='Field 2', value='dolor sit') 
webhook.add_embed(embed)
#"""
res = webhook.execute()
print(res)
print(res.json())
#"""