from sqlalchemy import Column, String, Integer
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker


engine = create_engine("mysql+pymysql://root:root@localhost:3306/song_message", echo=True)
Session = sessionmaker(bind=engine)
session = Session()

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
    password = Column(String(20))

    def __repr__(self):
        ID = self.id
        NAME = self.name
        PASSWORD = self.password
        return f"User: id: {ID}, name:{NAME},password:{PASSWORD} "


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

def get_sheet():
    {
    Base.metadata.create_all(engine)  # 通过此语句创建表
}