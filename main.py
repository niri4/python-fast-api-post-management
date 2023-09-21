from fastapi import FastAPI, Request, HTTPException, Depends, status
from typing import Annotated
import models
import bcrypt
from database import engine, SessionLocal
from models_schema import PostSchema, UserSchema, UserLoginSchema
from sqlalchemy.orm import Session
from auth.auth_bearer import JWTBearer
from auth.auth_handler import signJWT, decodeJWT
from fastapi_cache import FastAPICache
from fastapi_cache.backends.redis import RedisBackend
from fastapi_cache.decorator import cache

from redis import asyncio as aioredis

app = FastAPI()

CONTENT_MAXIMUM_SIZE = 1_000_000 # 1mb

@cache()
async def get_cache():
  return 1

@app.on_event("startup")
async def startup():
  redis = aioredis.from_url("redis://localhost", encoding="utf8", decode_responses=True)
  FastAPICache.init(RedisBackend(redis), prefix="fastapi-cache")

models.Base.metadata.create_all(bind=engine)

def get_db():
  db = SessionLocal()
  try:
    yield db
  finally:
    db.close()

db_dependency = Annotated[Session, Depends(get_db)]

def __validate_content_length(headers):
  if 'content-length' not in headers:
    return [False, status.HTTP_411_LENGTH_REQUIRED]
  content_length = int(headers['content-length'])
  if content_length > CONTENT_MAXIMUM_SIZE:
    return [False, status.HTTP_413_REQUEST_ENTITY_TOO_LARGE]
  
  return [True, status.HTTP_200_OK]

def __checkuser(user, usr):
  if usr is not None:
    if __validate_password(usr.password, user.password):
      return True
    else:
      return False
  else:
    return False

def __password_encrypt(password):
  bytes = password.encode('utf-8')
  salt = bcrypt.gensalt()
  return bcrypt.hashpw(bytes, salt)

def __validate_password(password, userpassword):
  userBytes = userpassword.encode('utf-8')
  return bcrypt.checkpw(userBytes, password)

@app.get("/posts", tags=["posts"], dependencies=[Depends(JWTBearer())], status_code=status.HTTP_200_OK)
@cache(expire=300)
async def get_posts(request: Request, db: db_dependency) -> list[PostSchema]:
  token = request.headers['Authorization']
  user_id = decodeJWT(token.replace("Bearer ", ""))['user_id']
  posts = db.query(models.Post).filter(models.Post.user_id == user_id)
  return posts

@app.get("/posts/{post_id}", tags=["posts"], dependencies=[Depends(JWTBearer())], status_code=status.HTTP_200_OK)
async def get_post(post_id: int, db: db_dependency) -> PostSchema:
  post = db.query(models.Post).filter(models.Post.id == post_id).first()
  if post is not None:
    return post
  else:
    raise HTTPException(status_code= status.HTTP_404_NOT_FOUND, detail="Post not found")

@app.delete("/posts/{post_id}", tags=["posts"], dependencies=[Depends(JWTBearer())], status_code=status.HTTP_200_OK)
async def delete_post(post_id: int, db: db_dependency) -> None:
  post = db.query(models.Post).filter(models.Post.id == post_id).first()
  if post is not None:
    db.delete(post)
    db.commit()
  else:
    raise HTTPException(status_code= status.HTTP_404_NOT_FOUND, detail="Post not found")

@app.post("/posts", tags=["posts"], dependencies=[Depends(JWTBearer())], status_code=status.HTTP_201_CREATED)
async def add_post(request: Request, db: db_dependency, post: PostSchema) -> dict:
  content_length_status, status_code = __validate_content_length(request.headers)
  if content_length_status:
    db_post = models.Post(**post.model_dump())
    token = request.headers['Authorization']
    db_post.user_id = decodeJWT(token.replace("Bearer ", ""))['user_id']
    try:
      db.add(db_post)
      db.commit()
      return { "id": db_post.id }
    except:
      raise HTTPException(status_code= status.HTTP_422_UNPROCESSABLE_ENTITY, detail="Post not created successfully")
  else:
    raise HTTPException(status_code= status_code, detail="Post content length exceed 1MB of size")
    
@app.post("/signup", tags=["user"], status_code=status.HTTP_201_CREATED)
async def create_user(db: db_dependency, user: UserSchema) -> dict:
  db_user = models.User(**user.model_dump())
  db_user.password = __password_encrypt(db_user.password)
  try:
    db.add(db_user)
    db.commit()
    return signJWT(db_user.id)
  except:
    return { "error": "Sign up failed" }

@app.post("/login", tags=["user"], status_code=status.HTTP_200_OK)
async def user_login(db: db_dependency, user: UserLoginSchema) -> dict:
  usr = db.query(models.User).filter(models.User.email == user.email).first()
  if __checkuser(user, usr):
    return signJWT(usr.id)
  raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Wrong login details!")