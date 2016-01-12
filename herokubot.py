from flask import Flask,request
import json
import requests
import re
import os

app = Flask(__name__)
rpattern = r'^\/(?P<command>.*) (?P<q>.*)'

def naver_movie(q,data):
    url = "http://auto.movie.naver.com/ac"
    params = {"q_enc":"UTF-8","st":"1","r_lt":"1","n_ext" : "1","t_koreng":"1","r_format":"json","r_enc":"UTF-8",
            "r_unicode":"0","r_escape":"1","q":q}

    r = requests.get(url,params=params)
    contents = json.loads(r.content.decode("utf-8"))
    mv_poster_url = contents['items'][0][0][3][0]
    print(mv_poster_url)
    r= requests.get(mv_poster_url)
    with open("out.jpg","wb+") as f:
        f.write(r.content)
        f.seek(0)
        INFO = {"chat_id": data['message']['id']}
        files= {"photo" : f}
        r = requests.post("https://api.telegram.org/bot"+os.environ['TELEGRAM_TOKEN']+"/sendPhoto",files=files,data=INFO,stream=True)


@app.route('/')
def hello():
    return "hello"

@app.route('/'+os.environ['TELEGRAM_TOKEN']+'/',methods=["POST","GET"])
def token():
    if request.method == "POST":
        print(request.content_type)
        print("content_type")
        print(request.get_json())
        print("request.get_json()")
        getjson = request.get_json()
        print(getjson)
        print("before re")
        REresult = re.search(rpattern,getjson['message']['text'])
        print(REresult.group("command"))
        if REresult.group("command") == "poster":
            if REresult.group('q'):
                print(REresult.group('q'))
                INFO = {"chat_id": getjson['message']['id'],"text":"사용법 \n /poster 영화제목"}
                requests.get("https://api.telegram.org/bot"+os.environ['TELEGRAM_TOKEN']+"/sendMessage",params=INFO)
            naver_movie(REresult.group('q',getjson))
        else:
            return "notthing your command"

    return "Success"
