from flask import Flask, request
from threading import Thread
from commands.webhook import yt_webhook
import xmltodict
from xml.parsers.expat import ExpatError
from logger import getlog, writelog


app = Flask(__name__)


@app.route("/")
def lol():
    return "Hello..."


""" 
yt-to-discord - YouTube push notifications to Discord webhooks
Copyright (C) 2021  Bryan Cuneo

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU Affero General Public License as
published by the Free Software Foundation, either version 3 of the
License, or (at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU Affero General Public License for more details.

You should have received a copy of the GNU Affero General Public License
along with this program.  If not, see <http://www.gnu.org/licenses/>.

webhook_url: YOUR WEBHOOK URL HERE

channel_ids: []

message_prefix:
"""


@app.route("/feed", methods=["GET", "POST"])
def feed():
    """Accept and parse requests from YT's pubsubhubbub.
    https://developers.google.com/youtube/v3/guides/push_notifications
    """

    writelog("entry")
    challenge = request.args.get("hub.challenge")
    if challenge:
        # YT will send a challenge from time to time to confirm the server is alive.
        writelog("challenged")
        return challenge

    try:
        # Parse the XML from the POST request into a dict.
        xml_dict = xmltodict.parse(request.data)

        # Lazy verification - check if the POST request is from a channel ID that's been
        # set in config["channel_ids"].  Skip the check if that config option is empty.
        channel_id = xml_dict["feed"]["entry"]["yt:channelId"]
        if channel_id not in ["UCyjy3LTL7AIV_Iwf4A9PeGw"]:
            writelog("channelid error", obj=xml_dict)
            return "", 403

        # Parse out the video URL.
        video_url = xml_dict["feed"]["entry"]["link"]["@href"]
        if video_url not in getlog():
            yt_webhook(check_old=True)
            writelog(f"New video URL: {video_url}")
        # # Send the message to the webhook URL.
        # # https://discord.com/developers/docs/resources/webhook
        # message = config["message_prefix"] + "\n" + video_url
        # webhook = DiscordWebhook(url=os.environ['webhook_url'], content=message)
        # response = webhook.execute()

    except (ExpatError, LookupError):
        writelog("malformed/no data", obj=xml_dict)
        # request.data contains malformed XML or no XML at all, return FORBIDDEN.
        return "", 403

    # Everything is good, return NO CONTENT.
    return "", 204


def run():
    app.run("0.0.0.0", port=20548)


def keep_alive():
    t1 = Thread(target=run)
    t1.start()
    return t1
