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
    elif request.method == "GET":
        getjson = request.get_json()
        print(getjson)
    return "Success"


def get_image(chat_id, text):
    url = "https://apis.daum.net/search/image"
    params = {'q': text, 'result': 20, 'pageno': 1, 'sort': 'accu',
               'output':'json', 'apikey': os.environ['DAUM_API']}
    inlineQRP = list()
    r = requests.get(url, params=params)
    r = r.json()

    for data in r['channel']['item']:
        inlineQRP.append([{"type": "photo", "id": text,
                           "photo_url": data['image'],
                           "thumbnail_url": data['thumbnail']}])

    r = requests.post("https://api.telegram.org/bot" +
                       os.environ['TELEGRAM_TOKEN'] + "/InlineQueryResultPhoto",
                       json=info)
