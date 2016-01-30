from bs4 import BeautifulSoup
import sqlite3
from datetime import datetime
from pytz import timezone
import requests
import transmissionrpc
from apscheduler.schedulers.blocking import BlockingScheduler
from os import environ


tc=transmissionrpc.Client(address=environ["TRANSMISSON_URL"],port=environ["TRANSMISSON_PORT"],
                          user=environ["TRANSMISSON_ID"],password=environ["TRANSMISSON_PW"])

telegram_body = {'message': {'date': 1453276318,
                             'message_id': 162,
                             'chat': {'username': 'yangbeom',
                                      'type': 'private',
                                      'id': 148229544,
                                      'first_name': 'yangbeom'},
                             'text': '/transmission',
                             'from': {'username': 'yangbeom',
                                      'id': 148229544,
                                      'first_name': 'yangbeom'}
                             },
                 'update_id': 893847671}
sched = BlockingScheduler(timezone=environ["TZ"])


def get_url(keywords, genre):
    tosarang_base_url = "http://www.tosarang2.net/bbs/board.php?bo_table="
    tosarang_search_option = "&sfl=wr_subject&stx=WITH+720p+"
    ENT = "torrent_kortv_ent"
    DRA = "torrent_kortv_drama"
    if genre == "ent":
        tosarang_url = tosarang_base_url+ENT+tosarang_search_option+keywords
    elif genre == "drama":
        tosarang_url = tosarang_base_url+DRA+tosarang_search_option+keywords

    r = requests.get(tosarang_url)
    bs = BeautifulSoup(r.content, "html.parser")
    result = bs.find("td", attrs={'class': 'td_subject'})

    return result.a.text, result.a.get("href")

def get_magnet(url):
    r = requests.get(url)
    bs = BeautifulSoup(r.content, "html.parser")
    result = bs.find_all("div", attrs={'class': 'bo_v_file'})
    return result[1].a.text


@sched.scheduled_job("cron",day_of_week='mon-sun', hour= "10-12,12-15", minute= "*/1")
def search_torrent():
    conn = sqlite3.connect(environ["DB_NAME"])
    cur = conn.cursor()
    today =datetime.now(timezone(environ["TZ"])).date() #오늘의 날
    xml_soup = BeautifulSoup(open('downlist.xml',encoding='utf8'),'html.parser')
    for downdata in xml_soup.torrent.find_all(today.strftime("%a").lower()):
        for torrent in downdata.find_all("torrent"):
            cur.execute("select date from magnet where title = ?", (torrent.subject.text,))
            db_date = cur.fetchone()
            if db_date is None:
                print("db_date is None")
                title, url = get_url(keywords=torrent.subject.text, genre=torrent.genre.text)
                title = title.split(".")
                magnet = get_magnet(url)
                cur.execute("insert or replace into magnet (title,date) values(?,?)", (title[0], title[2]))
                conn.commit()
                tc.add_torrent(magnet, download_dir=torrent.dir.text)
                telegram_body['message']['text'] = "/transmission "+title[0]+"다운로드 시작"
                requests.post("https://yangbeombot.herokuapp.com/"+environ['TELEGRAM_TOKEN'],
                                  json=telegram_body)
            elif  db_date is not None and db_date !="END":
                db_date = datetime.strptime(db_date[0],"%y%m%d").date()
                title, url = get_url(keywords=torrent.subject.text, genre=torrent.genre.text)
                title = title.split(".")
                today = datetime.strptime(title[2],"%y%m%d").date()
                if today>db_date or today.lower() == "end":
                    magnet = get_magnet(url)
                    cur.execute("insert or replace into magnet (title,date) values(?,?)", (title[0], title[2]))
                    conn.commit()
                    tc.add_torrent(magnet, download_dir=torrent.dir.text)
                    telegram_body['message']['text'] = "/transmission "+title[0]+"다운로드 시작"
                    requests.post("https://yangbeombot.herokuapp.com/"+environ['TELEGRAM_TOKEN'],
                                  json=telegram_body)
    conn.close()


sched.start()
