from flask import Flask, request
import json
import requests
import re
import os

app = Flask(__name__)
rcommand = r'^\/(?P<command>\w*)'
rpattern = r'^\/(?P<command>\w*) (?P<q>.*)'


@app.route('/', methods=["POST", "GET"])
def token():
    if request.method == "POST":
        getjson = request.get_json()
        print(getjson)
        if "inline_query" in getjson.keys():
            print("get inline")
            get_image(getjson['inline_query']['id'], getjson['inline_query']['query'])
        elif "message" in getjson.keys():
            print("get message")
            print(getjson['message']['from']['id'])
            sendM = {"chat_id": getjson['message']['from']['id'], "text": "hi"}
            r = requests.post("https://api.telegram.org/bot" +
                       os.environ['TELEGRAM_TOKEN'] + "/sendmessage",
                       json=sendM)
            print(r.text)
            print(r.status_code)
    return "Success"


def get_image(chat_id, text):
    print("in get_image")
    url = "https://apis.daum.net/search/image"
    params = {'q': text, 'result': 20, 'pageno': 1, 'sort': 'accu',
              'output':'json', 'apikey': os.environ['DAUM_API']}
    inlineQRP = list()
    r = requests.get(url, params=params)
    r = r.json()
    inline_answer = {"inline_query_id": chat_id}
    for data in r['channel']['item']:
        inlineQRP.append({"type": "photo", "id": data['thumbnail'],
                "photo_url": data['image'], "thumb_url": data['thumbnail'],
                "photo_width": int(data['width']),
                "photo_height": int(data['height'])})

    inline_answer['results'] = inlineQRP
    print(inline_answer)
    r = requests.post("https://api.telegram.org/bot" +
                       os.environ['TELEGRAM_TOKEN'] + "/answerInlineQuery",
                       json=inline_answer)
    print(r.text)
