import requests

x = requests.post(
                 "https://pubsubhubbub.appspot.com/subscribe",
                 data = {
                    "hub.callback": "https://custom-discord-bot.quantumcodes.repl.co/feed",
                    "hub.topic": "https://www.youtube.com/xml/feeds/videos.xml?channel_id=UCyjy3LTL7AIV_Iwf4A9PeGw",
                    "hub.verify": "sync",
                    "hub.mode": "subscribe",
                    "hub.verify_token": "",
                    "hub.secret": "",
                    "hub.lease_numbers": ""
                 }
)

print(x)
print(vars(x), "\n")
print(x.text, "\n")

if x.status_code != 204:
  print(1 + "yes I need an error for this to be in my notifications")