from pydantic import BaseModel


class AuthBase(BaseModel):
    email: str


class AuthVerify(AuthBase):
    password: str


class AuthCreate(AuthVerify):
    name: str


class AuthNewPassword(AuthVerify):
    new_password: str


class Auth(AuthBase):
    id: int

    class Config:
        from_attributes = True
