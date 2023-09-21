from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base
from decouple import config

URI_DATABASE = "mysql+pymysql://root:niri@localhost:3306/postdatabase"
"mariadb+pymysql://{db_username}:{db_password}@{db_hostname}:{db_port}/{db_name}".format(
    db_username= config("db_username"),
    db_password= config("db_password"),
    db_hostname = config("db_hostname"),
    db_port = config("db_port"),
    db_name = config("db_name")
  )

engine = create_engine(URI_DATABASE)
SessionLocal = sessionmaker(autocommit=False, bind=engine)

Base = declarative_base()