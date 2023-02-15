import requests
from flask import send_from_directory, make_response,Blueprint
from flask import Flask, request, jsonify
from sqlalchemy import Column, String, Integer
from sqlalchemy.ext.declarative import declarative_base
from datetime import timedelta, datetime
import jwt
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from flask_cors import CORS

from data_sheet import Data, Down, session
from id import len_list, cont_down_up, get_cont_down, get_cont_down_list, del_cont_down_list

cont = 0
id = 0
cont_down = 0
cont_down_list = []


#通过spider完成信息爬取和歌曲下载
class Spider:
    def __init__(self):
        self.headers = {'Accept': ',application/json, text/plain, */*',  # 请求头信息
                        'Accept-Encoding': 'gzip, deflate',
                        'Accept-Language': 'zh-CN,zh;q=0.9',
                        'Connection': 'keep-alive',
                        'Cookie': '_ga=GA1.2.1637941648.1616934252; uname3=qq1616934321; t3kwid=131286315; websid=1488073791; pic3=""; t3=qq; Hm_lvt_cdb524f42f0ce19b169a8071123a4797=1617949101,1618127723,1618579672,1619099581; _gid=GA1.2.1505163314.1619099581; Hm_lpvt_cdb524f42f0ce19b169a8071123a4797=1619100738; _gat=1; kw_token=XM5GXCP8M5',
                        'csrf': 'XM5GXCP8M5',
                        'Host': 'www.kuwo.cn',
                        'Referer': 'http://www.kuwo.cn/search/list?key=%E5%91%A8%E6%9D%B0%E4%BC%A6',
                        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/70.0.3538.25 Safari/537.36 Core/1.70.3861.400 QQBrowser/10.7.4313.400'}

    def get_song(self, my_url, singer):
        url = my_url
        response = requests.get(url, headers=self.headers)
        json = response.json()  # 得到储存歌曲信息的json文件,下面是层层解析获取name和rid
        data = json.get("data")
        song_list = data.get("list")
        song_message = []
        for song in song_list:
            song_name = song['name']
            song_album = song['album']
            song_artist = song['artist']
            song_rid = song['rid']
            seconds = song['duration']
            m, s = divmod(seconds, 60)
            song_t = str(int(m)).zfill(2) + ":" + str(int(s)).zfill(2)
            song_json_url = 'http://www.kuwo.cn/url?format=mp3&rid={}&response=url&type=convert_url3&br=128kmp3&from=web&t=1619102008389&httpsStatus=1&reqId=b4280751-a377-11eb-a99d-ef0323beeee3'.format(
                song_rid)  # 不断改变rid以获取不同歌取的mp3地址
            song_message.append(
                {"name": song_name, "album": song_album, "duration": song_t, "artist": song_artist, "rid": song_rid})
            global cont
            result = session.query(Data).filter(Data.rid == song_rid).first()
            if result is None:
                Newsong = Data(id=cont, rid=song_rid, fav=0, duration=song_t, album=song_album,
                            artist=song_artist, name=song_name, down=0
                            )
                session.add(Newsong)
                session.commit()
        return song_message

    def file(self, rid):
        path = session.query(Data).filter(Data.rid == rid).first().name + ".mp3"
        url = "https://link.hhtjim.com/kw/" + str(rid) + ".mp3"
        with open(path, "wb") as f:
            f.write(requests.get(url).content)
        f.close()
        cont_down_up()
        if session.query(Down).filter(Down.rid==rid).first() == None:
            n = get_cont_down()
            if len_list() != 0:
                n = get_cont_down_list()
                del_cont_down_list()
            Newsong = Down(rid=rid,page=n/30+1)
            session.add(Newsong)
            session.commit()
            song = session.query(Data).filter(Data.rid==rid).first()
            song.page = n/30+1
            song.down = 1
            session.add(song)
            session.commit()

        return send_from_directory('', path)