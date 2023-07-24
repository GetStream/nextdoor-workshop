import functools
import time

from flask import Flask, request, abort
from flask_cors import cross_origin
import stream_chat
import os

from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)

api_key = os.getenv("STREAM_API_KEY")
api_secret = os.getenv("STREAM_API_SECRET")

token_ttl_in_seconds = 3600

client = stream_chat.StreamChat(
    api_key=api_key,
    api_secret=api_secret,
)


def members_from_data(data):
    members = [
        dict(user=dict(id=uid, **user_data))
        for uid, user_data in data["members"].items()
    ]
    # ensure the users involved in this channel exist
    client.upsert_users(users=[m["user"] for m in members])
    return members


def api_error_response(f):
    @functools.wraps(f)
    def wrapped():
        try:
            return f()
        except stream_chat.client.StreamAPIException as e:
            return {"api_error": str(e)}

    return wrapped


@app.route("/message", methods=["POST"])
@api_error_response
def sync_message():
    """
    This endpoint ensures that a new message is created on Stream including users and channel
    """
    data = request.json
    message = data["message"]
    members = members_from_data(data)

    channel = client.channel(
        "messaging",
        data={
            "members": members,
        },
    )

    channel.create(
        data["channel"]["creator_id"], **data["channel"].get("custom_data", {})
    )

    return channel.send_message(
        {"id": message["id"], "text": message["text"]}, user_id=data["user"]["id"]
    )


@app.route("/channel", methods=["POST"])
@api_error_response
def sync_channel():
    """
    This endpoint ensures that a new channel is created on Stream including users and channel
    """

    data = request.json
    members = members_from_data(data)

    client.upsert_users(users=[m["user"] for m in members])
    channel = client.channel(
        "messaging",
        data={
            "members": members,
        },
    )
    return channel.create(
        data["channel"]["creator_id"], **data["channel"].get("custom_data", {})
    )


@app.route("/generate-token", methods=["POST"])
@cross_origin()
def generate_token():
    """
    Generates a user token to connect to Stream Chat

    curl -i -H "Content-Type: application/json" -X POST -d '{"user_id": "tommaso"}' http://localhost:5000/generate-token
    """

    # NOTE: this is just an example app using staging credentials and is only suitable for a test environment
    # a real application must not blindly generate a token for a user!
    user_id = request.json.get("user_id")

    token = client.create_token(
        user_id,
        exp=int(time.time()) + token_ttl_in_seconds,
    )
    return {"token": token}


@app.route("/stream-incoming-wh", methods=["POST"])
def webhook_handler():
    """
    This endpoint receives JSON encoded payloads for all chat events as they occurred on Stream Chat and writes them back
    to the primary chat system so that chats stay in-sync.

    Relevant documentation about webhook events can be found [here](https://getstream.io/chat/docs/python/webhooks_overview/?language=python)

    Webhook payloads from Stream include a signature header that can be verified using the shared API Secret
    further hardening can be achieved by exposing this service to Stream static list of public IPs
    the allow list is documented [here](https://getstream.io/chat/docs/python/webhooks_overview/?language=python)
    """

    if not client.verify_webhook(request.data, request.headers["X-SIGNATURE"]):
        abort(401, description="Payload did not contain a valid signature.")

    payload = request.json

    if payload["type"] == "message.new":
        # TODO: insert the message back to primary chat system
        pass

    return ""


if __name__ == "__main__":
    app.run(host="0.0.0.0")
