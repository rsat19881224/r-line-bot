# -*- coding: utf-8 -*-

#  Licensed under the Apache License, Version 2.0 (the "License"); you may
#  not use this file except in compliance with the License. You may obtain
#  a copy of the License at
#
#       https://www.apache.org/licenses/LICENSE-2.0
#
#  Unless required by applicable law or agreed to in writing, software
#  distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
#  WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
#  License for the specific language governing permissions and limitations
#  under the License.

import json
import os
import sys
import re
from argparse import ArgumentParser

from flask import Flask, request, abort
from jinja2 import Environment, FileSystemLoader, select_autoescape
from linebot import (
    LineBotApi, WebhookHandler
)
from linebot.exceptions import (
    InvalidSignatureError,LineBotApiError
)
from linebot.models import (
    MessageEvent, TextMessage, TextSendMessage,FlexSendMessage, BubbleContainer, CarouselContainer
)

app = Flask(__name__)

# LINE連携部分 #
# get channel_secret and channel_access_token from your environment variable
channel_secret = os.getenv('LINE_CHANNEL_SECRET', None)
channel_access_token = os.getenv('LINE_CHANNEL_ACCESS_TOKEN', None)
if channel_secret is None:
    print('Specify LINE_CHANNEL_SECRET as environment variable.')
    sys.exit(1)
if channel_access_token is None:
    print('Specify LINE_CHANNEL_ACCESS_TOKEN as environment variable.')
    sys.exit(1)
line_bot_api = LineBotApi(channel_access_token)
handler = WebhookHandler(channel_secret)

# テスト用 #
@app.route("/")
def hello_world():
    return "hello world!"

# LINE メッセージ受信時処理 #
@app.route("/callback", methods=['POST'])
def callback():
    # get X-Line-Signature header value
    signature = request.headers['X-Line-Signature']

    # get request body as text
    body = request.get_data(as_text=True)
    app.logger.info("Request body: " + body)

    # handle webhook body
    try:
        handler.handle(body, signature)
    except InvalidSignatureError:
        abort(400)
    except LineBotApiError as e:
        app.logger.exception(f'LineBotApiError: {e.status_code} {e.message}', e)
        raise e
    return 'OK'

@handler.add(MessageEvent, message=TextMessage)
def handle_message(event):
    global near_station_name
    global near_station_address
    global near_station_geo_lat
    global near_station_geo_lon

    if event.type == "message":
        if (event.message.text == "帰るよー！") or (event.message.text == "帰るよ！") or (event.message.text == "帰る！") or (event.message.text == "帰るよ"):
            line_bot_api.reply_message(
                event.reply_token,
                [
                    TextSendMessage(text='お疲れ様です'+ chr(0x10002D)),
                    TextSendMessage(text='位置情報を送ってもらうと近くの駅を教えますよ'+ chr(0x10008D)),
                    TextSendMessage(text='line://nv/location'),
                ]
            )
        if (event.message.text == "ありがとう！") or (event.message.text == "ありがとう") or (event.message.text == "ありがと！") or (event.message.text == "ありがと"):
            line_bot_api.reply_message(
                event.reply_token,
                [
                    TextSendMessage(text="どういたしまして！気をつけて帰ってね" + chr(0x100033)),
                ]
            )
        if event.message.text == "位置情報教えて！":
            line_bot_api.reply_message(
                event.reply_token,
                [
                    LocationSendMessage(
                        title=near_station_name,
                        address=near_station_address,
                        latitude=near_station_geo_lat,
                        longitude=near_station_geo_lon
                    ),
                    TextSendMessage(text="タップした後右上のボタンからGoogleMapsなどで開けますよ"+ chr(0x100079)),
                    TextSendMessage(text="もし場所が間違えてたらもう一度地図画像をタップしてみたり位置情報を送り直してみてください"),    
                ]
            )
        else:
            line_bot_api.reply_message(
                event.reply_token,
                [
                    TextSendMessage(text="まだその言葉は教えてもらってないんです"+ chr(0x100029) + chr(0x100098)),
                ]
            )




if __name__ == "__main__":
#    app.run()
    port = int(os.getenv("PORT", 5000))
    app.run(host="0.0.0.0", port=port)