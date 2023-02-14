import requests
from flask import send_from_directory, make_response
from flask import Flask, request, jsonify
from sqlalchemy import Column, String, Integer
from sqlalchemy.ext.declarative import declarative_base
from datetime import timedelta, datetime
import jwt
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from flask_cors import CORS


app = Flask(__name__)
CORS(app, supports_credentials=True)

SECRET_KEY: str = "sdifhgsiasfjaofhslio"  # JWY签名所使用的密钥，是私密的，只在服务端保存
ALGORITHM = "HS256"  # 加密算法，我这里使用的是HS256

engine = create_engine("mysql+pymysql://root:root@localhost:3306/song_message", echo=True)
Session = sessionmaker(bind=engine)
session = Session()

#data和down的id
cont = 0
id = 0
cont_down = 0
cont_down_list = []

Base = declarative_base()

#表信息
class Down(Base):
    __tablename__ = "down"
    id = Column(Integer,primary_key=True)
    rid = Column(Integer)
    page = Column(Integer)

    def __repr__(self):
        ID = self.id
        RID = self.rid
        PAGE = self.page
        return f"User: rid: {RID},page:{PAGE},id: {ID}"

class User(Base):
    __tablename__ = "user"
    id = Column(Integer, primary_key=True)
    name = Column(String(20))

    def __repr__(self):
        ID = self.id
        NAME = self.name
        return f"User: id: {ID}, name:{NAME} "


class Data(Base):
    __tablename__ = "data"
    id = Column(Integer, primary_key=True)
    rid = Column(Integer)
    fav = Column(Integer)
    page = Column(Integer)
    down =  Column(Integer)
    duration = Column(String(20))
    album = Column(String(50))
    artist = Column(String(50))
    name = Column(String(50))

    def __repr__(self):
        PAGE = self.page
        ID = self.id
        RID = self.rid
        FAV = self.fav
        DURATION = self.duration
        ALBUM = self.album
        ARTIST = self.artist
        NAME = self.name
        DOWN = self.down
        return f"User: id: {ID}, rid: {RID}, fav: {FAV}, duration:{DURATION}, album:{ALBUM},artist:{ARTIST}, name:{NAME},down:{DOWN},page:{PAGE} "

Base.metadata.create_all(engine)	# 通过此语句创建表

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
        global cont_down
        global cont_down_list
        cont_down += 1
        if session.query(Down).filter(Down.rid==rid).first() == None:
            n = cont_down
            if len(cont_down_list) != 0:
                n = cont_down_list[0]
                del cont_down_list[0]
            Newsong = Down(rid=rid,page=n/30+1)
            session.add(Newsong)
            session.commit()
            song = session.query(Data).filter(Data.rid==rid).first()
            song.page = n/30+1
            song.down = 1
            session.add(song)
            session.commit()

        return send_from_directory('', path)


#检验token
def cheak_token(token):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        print(username)
        if username == "123":
            return username
    except jwt.PyJWTError:
        return jsonify(dict(code=401, message="认证失败，请重试"))


@app.route("/user", methods=["POST"])
def enroll():
    global id
    username = request.json.get("username")
    password = request.json.get("password")
    checkPassword = request.json.get("checkPassword")
    if checkPassword == password:
        results = session.query(User).filter(User.name == username).first()
        if results is None:
            id += 1
            NewUser = User(name=username, id=id)
            session.add(NewUser)
            session.commit()
            return jsonify(dict(token_type="bearer", code=200, message="success",
                            data={"id": id, "username": username}))
        return jsonify(dict(message="该账号已被注册"))
    return  jsonify(dict(message="请重新输入"))


@app.route("/user/login", methods=["POST"])
def login():
    # 从json中获取数据
    my_json = request.get_json()
    username = my_json.get("username")
    password = my_json.get("password")
    result = session.query(User).filter(User.name==username).first()
    if result is None:
        return jsonify(dict(message="该账号未注册"))
    try:
        access_token_expires = timedelta(minutes=60)
        expire = datetime.utcnow() + access_token_expires
        payload = {
            "sub": username,
            "exp": expire
        }
        access_token = jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)
    except Exception as e:
        print(e)
        return jsonify(dict(code=401, exception=e))
    if username and password:
        return jsonify(dict(token_type="bearer", code=200, message="success",
                            data={"id": 1, "username": "admin", "token": access_token}))
    else:
        return jsonify((dict(code=401, message="请输入用户名和密码")))


@app.route("/search", methods=["GET"])
def search():
    # 从json中获取数据
    text = request.args.get("text")
    token = request.headers.get("Authorization")
    username = cheak_token(token)
    print(username)
    print(token)
    if username is not None:
        print(username)
    else:
        return jsonify(dict(code=403, message="无法检验token"))
    music = Spider()
    artist_json = music.get_song(
        "http://www.kuwo.cn/api/www/search/searchMusicBykeyWord?key=" + text + "&pn=1&rn=30&httpsStatus=1&reqId=b4274401-a377-11eb-a99d-ef0323beeee3",
        text)
    return jsonify(dict(code=200,message="success",data={"list":artist_json}))


@app.route("/search/download/<rid>", methods=["GET"])
def download(rid):
    token = request.headers.get("Authorization")
    username = cheak_token(token)
    if username is None:
        return jsonify(dict(code=403, message="无法检验token"))
    url = "http://www.kuwo.cn/play_detail/" + str(rid)
    music = Spider()
    path = music.file(rid)
    return path

#delete中步骤i相同，进行封装
def delete_one(ID):
    cont_down_list.append(ID)
    result = session.query(Down).filter(Down.id == ID).first()
    rid = result.rid
    session.delete(result)
    session.commit()
    result = session.query(Data).filter(Data.rid == rid).first()
    result.down = 0
    session.add(result)
    session.commit()

#完成删除操作
def delete(request):
    rsp = make_response("json")
    rsp.headers['Content-Type'] = 'application/json'
    token = request.headers.get("Authorization")
    type = request.json.get("type")
    ID = request.json.get("id")
    list = request.json.get("list")
    if type is 0:
        delete_one(ID)
    else:
        for ID in list:
            delete_one(ID)
    return jsonify(dict(code=200, message="success"))

#获取历史记录
def read(result_list):
    message = []
    for result in result_list:
        ID = session.query(Down).filter(Down.rid==result.rid).first().id
        result = {"id": ID, "rid": result.rid, "fav": result.fav, "duration": result.duration,
                  "album": result.album, "artist": result.artist, "name": result.name}
        message.append(result)
    return jsonify(dict(code=200, message="seccess", data={"list": message}))


#根据HTTp请求跳转不同方式
@app.route("/user/history", methods=["DELETE", "GET"])
def history():
    token = request.headers.get("Authorization")
    username = cheak_token(token)
    if not username or token is None:
        return jsonify(dict(code=403, message="无法检验token"))
    if request.method == "DELETE":
        result = delete(request)
        return result
    else:
        page = request.args.get("page")
        result_list = session.query(Data).filter(Data.page == page).filter(Data.down == 1).all()
        result = read(result_list)
        return result


@app.route("/user/history/lc", methods=["PUT"])
def lc():
    page = request.args.get("page")
    token = request.headers.get("Authorization")
    username = cheak_token(token)
    if not username or token is None:
        return jsonify(dict(code=403, message="无法检验token"))
    id = request.json.get("id")
    fav = request.json.get("fav")
    result = session.query(Data).filter(Data.id == id).first()
    result.fav = fav
    session.add(result)
    session.commit()
    result = {"name": result.name, "artist": result.artist, "album": result.album, "duration": result.duration,
              "rid": result.rid}
    return jsonify(dict(code=200, message="success", data=result))


app.run(host="0.0.0.0", port=8000)
