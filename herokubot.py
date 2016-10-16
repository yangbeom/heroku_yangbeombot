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
    return "Success"


def get_image(chat_id, text):
    print("in get_image")
    url = "https://apis.daum.net/search/image"
    params = {'q': text, 'result': 20, 'pageno': 1, 'sort': 'accu',
              'output':'json', 'apikey': os.environ['DAUM_API']}
    inlineQRP = list()
    r = requests.get(url, params=params)
    r = r.json()
    inline_answer = {"inline_query_id": chat_id, "results": []}
    for data in r['channel']['item']:
        inlineQRP.append([{"type": "photo", "id": text,
                           "photo_url": data['image'],
                           "thumbnail_url": data['thumbnail']}])

    inline_answer['results'].append(inlineQRP)
    print(inlineQRP)
    r = requests.post("https://api.telegram.org/bot" +
                       os.environ['TELEGRAM_TOKEN'] + "/answerInlineQuery",
                       json=inline_answer)
    print(r.text)