import requests
from flask import send_from_directory, make_response
from flask import Flask, request, jsonify,Blueprint
from sqlalchemy import Column, String, Integer
from sqlalchemy.ext.declarative import declarative_base
from datetime import timedelta, datetime
import jwt
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from flask_cors import CORS

from cheak_token import cheak_token
from spider import Spider

bp = Blueprint("search", __name__, url_prefix="/search")

@bp.route("", methods=["GET"])
def search():
    # 从json中获取数据
    text = request.args.get("text")
    token = request.headers.get("Authorization")
    username = cheak_token(token)
    if username is not None:
        print(request.method)
        print(username)
    else:
        return jsonify(dict(code=403, message="无法检验token"))
    music = Spider()
    artist_json = music.get_song(
        "http://www.kuwo.cn/api/www/search/searchMusicBykeyWord?key=" + text + "&pn=1&rn=30&httpsStatus=1&reqId=b4274401-a377-11eb-a99d-ef0323beeee3",
        text)
    return jsonify(dict(code=200,message="success",data={"list":artist_json}))


@bp.route("/download/<rid>", methods=["GET"])
def download(rid):
    token = request.headers.get("Authorization")
    username = cheak_token(token)
    if username is None:
        return jsonify(dict(code=403, message="无法检验token"))
    url = "http://www.kuwo.cn/play_detail/" + str(rid)
    music = Spider()
    path = music.file(rid)
    return path