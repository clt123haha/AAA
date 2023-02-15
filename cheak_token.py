import jwt
from flask import jsonify

from data_sheet import session, User

SECRET_KEY: str = "sdifhgsiasfjaofhslio"  # JWY签名所使用的密钥，是私密的，只在服务端保存
ALGORITHM = "HS256"  # 加密算法，我这里使用的是HS256

def cheak_token(token):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        result = session.query(User).filter(User.name==username)
        if result is not None:
            return username
    except jwt.PyJWTError:
        return jsonify(dict(code=401, message="认证失败，请重试"))