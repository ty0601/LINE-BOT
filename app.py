import os
import re
import sys
import transitions

from flask import Flask, jsonify, request, abort, send_file
from dotenv import load_dotenv
from linebot import LineBotApi, WebhookParser
from linebot.exceptions import InvalidSignatureError
from linebot.models import MessageEvent, TextMessage, TextSendMessage, StickerSendMessage, ImageSendMessage

from fsm import TocMachine
from utils import send_text_message

load_dotenv()

machine = TocMachine(
    states=["user", "menu", "coins", "coin_menu", "price", "metadata", "fsm_graph", "introduction", "cancel"],
    transitions=[
        {
            "trigger": "advance",
            "source": "user",
            "dest": "menu",
            "conditions": "is_going_to_menu",
        },
        {
            "trigger": "advance",
            "source": "menu",
            "dest": "menu",
            "conditions": "is_going_to_menu",
        },
        {
            "trigger": "advance",
            "source": "menu",
            "dest": "coins",
            "conditions": "is_going_to_coins",
        },
        {
            "trigger": "advance",
            "source": "coins",
            "dest": "menu",
            "conditions": "is_going_to_menu",
        },
        {
            "trigger": "advance",
            "source": "coins",
            "dest": "coin_menu",
            "conditions": "is_going_to_coin_menu",
        },
        {
            "trigger": "advance",
            "source": "coin_menu",
            "dest": "coins",
            "conditions": "is_going_to_coins",
        },
{
            "trigger": "advance",
            "source": "coin_menu",
            "dest": "price",
            "conditions": "is_going_to_price",
        },
{
            "trigger": "advance",
            "source": "coin_menu",
            "dest": "metadata",
            "conditions": "is_going_to_metadata",
        },
        {
            "trigger": "advance",
            "source": "menu",
            "dest": "introduction",
            "conditions": "is_going_to_introduction",
        },
        {
            "trigger": "advance",
            "source": "introduction",
            "dest": "menu",
            "conditions": "is_going_to_menu",
        },
        {
            "trigger": "advance",
            "source": "menu",
            "dest": "fsm_graph",
            "conditions": "is_going_to_fsm_graph",
        },
        {
            "trigger": "advance",
            "source": "price",
            "dest": "cancel",
            "conditions": "is_going_to_cancel",
        },
        {
            "trigger": "advance",
            "source": "price",
            "dest": "coins",
            "conditions": "is_going_to_coins",
        },
        {
            "trigger": "advance",
            "source": "metadata",
            "dest": "cancel",
            "conditions": "is_going_to_cancel",
        },
        {
            "trigger": "advance",
            "source": "metadata",
            "dest": "coins",
            "conditions": "is_going_to_coins",
        },

        {"trigger": "go_back", "source": ["fsm_graph", "cancel"], "dest": "user"},
    ],
    initial="user",
    auto_transitions=False,
    show_conditions=True,
)
app = Flask(__name__, static_url_path="")

# get channel_secret and channel_access_token from your environment variable
channel_secret = os.getenv("LINE_CHANNEL_SECRET", None)
channel_access_token = os.getenv("LINE_CHANNEL_ACCESS_TOKEN", None)
if channel_secret is None:
    print("Specify LINE_CHANNEL_SECRET as environment variable.")
    sys.exit(1)
if channel_access_token is None:
    print("Specify LINE_CHANNEL_ACCESS_TOKEN as environment variable.")
    sys.exit(1)

line_bot_api = LineBotApi(channel_access_token)
parser = WebhookParser(channel_secret)


@app.route("/callback", methods=["POST"])
def callback():
    signature = request.headers["X-Line-Signature"]
    # get request body as text
    body = request.get_data(as_text=True)
    app.logger.info("Request body: " + body)

    # parse webhook body
    try:
        events = parser.parse(body, signature)
    except InvalidSignatureError:
        abort(400)

    # if event is MessageEvent and message is TextMessage, then echo text
    for event in events:
        if not isinstance(event, MessageEvent):
            continue
        if not isinstance(event.message, TextMessage):
            continue
        line_bot_api.reply_message(
            event.reply_token, TextSendMessage(text=event.message.text)
        )
    return "OK"


@app.route("/webhook", methods=["POST"])
def webhook_handler():
    signature = request.headers["X-Line-Signature"]
    # get request body as text
    body = request.get_data(as_text=True)
    app.logger.info(f"Request body: {body}")

    # parse webhook body
    try:
        events = parser.parse(body, signature)
    except InvalidSignatureError:
        abort(400)

    # if event is MessageEvent and message is TextMessage, then echo text
    for event in events:
        if not isinstance(event, MessageEvent):
            continue
        if not isinstance(event.message, TextMessage):
            continue
        if not isinstance(event.message.text, str):
            continue
        print(f"\nFSM STATE: {machine.state}")
        print(f"REQUEST BODY: \n{body}")
        response = machine.advance(event)
        if not response:
            send_text_message(event.reply_token, "Not Entering any State")

    return "OK"


@app.route("/show-fsm", methods=["GET"])
def show_fsm():
    machine.get_graph().draw("fsm.png", prog="dot", format="png")
    return send_file("fsm.png", mimetype="image/png")


if __name__ == "__main__":
    port = os.environ.get("PORT", 8000)
    app.run(host="0.0.0.0", port=port, debug=True)
    show_fsm()
