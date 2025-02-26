from pydantic import BaseModel


class UserBase(BaseModel):
    email: str


class UserVerify(UserBase):
    password: str


class UserCreate(UserVerify):
    name: str


class UserNewPassword(UserVerify):
    new_password: str


class User(UserBase):
    id: int


class Config:
    orm_mode = True
