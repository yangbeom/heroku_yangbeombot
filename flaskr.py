from flask import Flask,request
import json
import requests
import re
import os

app = Flask(__name__)
rpattern = r'^\/(?P<command>.*) (?P<q>.*)'
def naver_movie(q):
    url = "http://auto.movie.naver.com/ac"
    params = {"q_enc":"UTF-8","st":"1","r_lt":"1","n_ext" : "1","t_koreng":"1","r_format":"json","r_enc":"UTF-8",
            "r_unicode":"0","r_escape":"1","q":q}

    r = requests.get(url,params=params)
    contents = json.loads(r.content.decode("utf-8"))
    mv_poster_url = contents['items'][0][0][3][0]
    r= requests.get(mv_poster_url)
    with open("out.jpg","wb+") as f:
        f.write(r.content)
        f.seek(0)
        INFO = {"chat_id": "148229544"}
        files= {"photo" : f}
        r = requests.post("https://api.telegram.org/"+os.environ['TELEGRAM_TOKEN']+"/sendPhoto",files=files,data=INFO,stream=True)


@app.route('/')
def hello():
    return "hello"

@app.route('/'+os.environ['TELEGRAM_TOKEN']+'/',methods=["POST","GET"])
def token():
    if request.method == "POST":
        print(request.content_type)
        print(request.get_json())
        getjson = json.loads(request.get_json())['result'][0]
        print(getjson)
        REresult = re.search(rpattern,getjson['message']['text'])
        print(REresult.group("command"))
        if REresult.group("command") == "poster":
            naver_movie(REresult.group('q'))
        else:
            return "notthing your command"

    return "Success"
