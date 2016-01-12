from flask import Flask, request
import json
import requests
import re
import os

app = Flask(__name__)
rpattern = r'^\/(?P<command>.*) (?P<q>.*)'
howtouse = """사용법
/poster 영화제목
영화 포스터를 전송합니다."""


def naver_movie(q, data):
    url = "http://auto.movie.naver.com/ac"
    params = {"q_enc": "UTF-8", "st": "1", "r_lt": "1", "n_ext": "1", "t_koreng": "1", "r_format": "json",
              "r_enc": "UTF-8", "r_unicode": "0", "r_escape": "1", "q": q}

    r = requests.get(url, params=params)
    contents = json.loads(r.content.decode("utf-8"))
    mv_poster_url = contents['items'][0][0][3][0]
    r = requests.get(mv_poster_url)
    with open("out.jpg", "wb+") as f:
        f.write(r.content)
        f.seek(0)
        info = {"chat_id": data['message']['from']['id']}
        files = {"photo": f}
        requests.post("https://api.telegram.org/bot"+os.environ['TELEGRAM_TOKEN']+"/sendPhoto", files=files,
                      data=info, stream=True)


@app.route('/')
def hello():
    return "hello"


@app.route('/'+os.environ['TELEGRAM_TOKEN']+'/', methods=["POST", "GET"])
def token():
    if request.method == "POST":
        getjson = request.get_json()
        try:
            reresult = re.search(rpattern, getjson['message']['text'])
            if reresult.group("command") == "poster":
                naver_movie(reresult.group('q'), getjson)
            else:
                return "notthing your command"
        except:
            info = {"chat_id": getjson['message']['from']['id'], "text": howtouse}
            requests.get("https://api.telegram.org/bot"+os.environ['TELEGRAM_TOKEN']+"/sendMessage", params=info)

    return "Success"
