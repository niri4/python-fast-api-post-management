from sqlalchemy import Text, Column, Integer, String
from database import Base

class User(Base):
  __tablename__ = "users"

  id = Column(Integer, primary_key=True, index=True, autoincrement=True)
  fullname= Column(String(255))
  email = Column(String(50), unique=True)
  password = Column(String(255))

class Post(Base):
  __tablename__ = "posts"

  id = Column(Integer, primary_key=True, index=True, autoincrement=True)
  title = Column(String(50))
  content = Column(Text)
  user_id = Column(Integer)