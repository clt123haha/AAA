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
from data_sheet import session, Down, Data
from id import list_append

bp = Blueprint("user_history", __name__, url_prefix="/user/history")



#delete中步骤i相同，进行封装
def delete_one(ID):
    list_append(ID)
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
@bp.route("", methods=["DELETE", "GET"])
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


@bp.route("/lc", methods=["PUT"])
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