from discord_webhook import DiscordWebhook
import os

def message():
  webhook = DiscordWebhook(url=os.environ["webhook_url"], content="please work")
  res = webhook.execute()
  return res

res = message()
print(res)
print(res.json())