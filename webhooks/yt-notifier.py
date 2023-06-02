from discord import Webhook
import aiohttp, os

async def message():
  async with aiohttp.ClientSession() as session:
    webhook = Webhook.from_url(os.environ["webhook_url"], session=session)
    await webhook.send("heyy")
    print("sent lol")