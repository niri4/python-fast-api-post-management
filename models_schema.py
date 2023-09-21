from pydantic import BaseModel, Field, EmailStr

class PostSchema(BaseModel):
  id: int = Field(default=None)
  title: str = Field(...)
  content: str = Field(...)

  class Config:
    json_schema_extra = {
      "example": {
        "title": "Securing FastAPI applications with JWT.",
        "content": "We'll be using PyJWT to sign, encode and decode JWT tokens...."
      }
    }

class UserSchema(BaseModel):
  fullname: str = Field(...)
  email: EmailStr = Field(...)
  password: str = Field(...)

  class Config:
    json_schema_extra = {
      "example": {
        "fullname": "abc",
        "email": "abc@example.com",
        "password": "weakpassword"
      }
    }

class UserLoginSchema(BaseModel):
  email: EmailStr = Field(...)
  password: str = Field(...)

  class Config:
    json_schema_extra = {
      "example": {
        "email": "abc@example.com",
        "password": "weakpassword"
      }
    }