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
def message_text(event):

    try:
        replied = text_pattern_handler.handle(event)

        if not replied:
            line_bot_api.reply_message(
                event.reply_token,
                # テキストメッセ返信処理 #
                TextSendMessage('ちょっと何言ってるかわからない')
            )

    except Exception:
        line_bot_api.reply_message(
            event.reply_token,
            TextSendMessage('エラーです')
        )
        raise

# auというキーワードが含まれたメッセージが来た場合の処理 #
@text_pattern_handler.add(pattern=r'^au$')
def reply_items(event: MessageEvent, match: Match):

    line_bot_api.reply_message(
        event.reply_token,
        # テキストメッセ返信処理 #
        TextSendMessage('au')
    )

    #items = msglst.get_items(10)

    #template = template_env.get_template('items.json')
    #data = template.render(dict(items=items))

    #print(data)

    #line_bot_api.reply_message(
    #    event.reply_token,
    #    FlexSendMessage(
    #        alt_text="items",
    #        contents=CarouselContainer.new_from_json_dict(json.loads(data))
    #    )
    #)



if __name__ == "__main__":
#    app.run()
    port = int(os.getenv("PORT", 5000))
    app.run(host="0.0.0.0", port=port)