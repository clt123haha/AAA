from flask import Blueprint
from cheak_token import SECRET_KEY, ALGORITHM
from data_sheet import session, User
from flask import request, jsonify
from datetime import timedelta, datetime
import jwt
from id import id_up, get_id

bp = Blueprint("user", __name__, url_prefix="/user")




@bp.route("", methods=["POST"])
def enroll():
    try:
        username = request.json.get("username")
        password = request.json.get("password")
        checkPassword = request.json.get("checkPassword")
        if checkPassword == password:
            results = session.query(User).filter(User.name == username).first()
            if results is None:
                id_up()
                NewUser = User(name=username, id=get_id(),password=password)
                session.add(NewUser)
                session.commit()
                return jsonify(dict(token_type="bearer", code=200, message="success",
                                    data={"id": get_id(), "username": username}))
            return jsonify(dict(message="该账号已被注册"))
        return jsonify(dict(message="请重新输入"))
    except Exception as e:
        print(e)


@bp.route("/login", methods=["POST"])
def login():
    # 从json中获取数据
    my_json = request.get_json()
    username = my_json.get("username")
    password = my_json.get("password")
    result = session.query(User).filter(User.name==username).filter(User.password==password).first()
    if result is None:
        return jsonify(dict(message="信息错误"))
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