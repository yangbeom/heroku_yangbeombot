from flask import Flask, request
import json
import requests
import re
import os

app = Flask(__name__)
rcommand = r'^\/(?P<command>\w*)'
rpattern = r'^\/(?P<command>\w*) (?P<q>.*)'


def how_to_use(jsondata):
    howtouse = """사용법
/poster 영화제목
영화 포스터를 전송합니다.
/weather
서울의 현재온도를 알려줍니다."""
    info = {"chat_id": jsondata['message']['from']['id'], "text": howtouse}
    requests.get("https://api.telegram.org/bot"+os.environ['TELEGRAM_TOKEN']+"/sendMessage", params=info)


def openweather(jsondata):
    r = requests.get("http://api.openweathermap.org/data/2.5/weather?id=1835848&units=metric&APPID="
                     +os.environ['OPENWEATHERMAP_KEY'])
    weatherdata = json.loads(r.content.decode("utf-8"))
    weatherinfo = "지역 : {} \n온도 : {}˚C\n습도 : {}%\n날씨 : {}".format(weatherdata['name'],
                                                                          weatherdata['main']['temp'],
                                                                          weatherdata['main']['humidity'],
                                                                          weatherdata['weather'][0]['main'])
    info = {"chat_id": jsondata['message']['chat']['id'], "text": weatherinfo}
    requests.get("https://api.telegram.org/bot"+os.environ['TELEGRAM_TOKEN']+"/sendMessage", params=info)


def naver_movie(q, jsondata):
    url = "http://auto.movie.naver.com/ac"
    params = {"q_enc": "UTF-8", "st": "1", "r_lt": "1", "n_ext": "1", "t_koreng": "1", "r_format": "json",
              "r_enc": "UTF-8", "r_unicode": "0", "r_escape": "1", "q": q}

    r = requests.get(url, params=params)
    contents = json.loads(r.content.decode("utf-8"))
    mv_poster_url = contents['items'][0][0][3][0]
    r = requests.get(mv_poster_url)
    print(mv_poster_url)
    with open("out.jpg", "wb+") as f:
        f.write(r.content)
        f.seek(0)
        info = {"chat_id": jsondata['message']['chat']['id']}
        files = {"photo": f}
        requests.post("https://api.telegram.org/bot"+os.environ['TELEGRAM_TOKEN']+"/sendPhoto", files=files,
                      data=info, stream=True)


def transmission(jsondata):
    print(jsondata)
    info = {"chat_id": jsondata['message']['chat']['id'], "text": jsondata['message']['text'].replace('/transmission',''), "parse_mode":"Markdown" }
    requests.get("https://api.telegram.org/bot"+os.environ['TELEGRAM_TOKEN']+"/sendMessage", params=info)

def testlocation(jsondata):
    print('def test send location')
    print(jsondata)
    location_button = {"text":"location","request_location":True}
    reply_keyboard = {"keyboard":[["text"],['hello']]}
    info = {"chat_id": jsondata['message']['chat']['id'],
            "text": "test location", "reply_markup":reply_keyboard}
    r = requests.post("https://api.telegram.org/bot" + os.environ['TELEGRAM_TOKEN'] + "/sendMessage", data=info)
    print(r.text)



@app.route('/'+os.environ['TELEGRAM_TOKEN']+'/', methods=["POST", "GET"])
def token():
    if request.method == "POST":
        getjson = request.get_json()
        print(getjson)
        try:
            reresult = re.search(rcommand, getjson['message']['text'])
            print(reresult.group("command"))
            if reresult:
                print(reresult.group("command"))
                if reresult.group("command") == "poster":
                    reresult = re.search(rpattern, getjson['message']['text'])
                    naver_movie(reresult.group('q'), getjson)
                elif reresult.group("command") == "weather":
                    openweather(getjson)
                elif reresult.group("command") == "transmission":
                    transmission(getjson)
                elif reresult.group("command") == "location":
                    testlocation(getjson)
                else:
                    how_to_use(getjson)
            else:
                how_to_use(getjson)
                return "notthing your command"
        except:
            return "what r u doing?"

    return "Success"

@app.route('/')
def hello():
    return "hello =)"
