from discord_webhook import DiscordWebhook
import os

webhook = DiscordWebhook(url=os.environ["webhook_url"], content="please work")
res = webhook.execute()
print(res)