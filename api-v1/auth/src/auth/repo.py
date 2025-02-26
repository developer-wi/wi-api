from fastapi import HTTPException
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from auth.model import User
from auth.scheme import UserCreate


class RepoUser(object):
    def __init__(self, DBSession: Session):
        self._session = DBSession

    def create(self, name: str, uuid: str, email: str, key: str):
        new_user = User(name=name, uuid=uuid, email=email, key=key)
        try:
            self._session.add(new_user)
            self._session.commit()
            self._session.refresh(new_user)
            return new_user
        except IntegrityError as e:
            self._session.rollback()
            err_msg = e.args[0]
            print(err_msg)
            if "Duplicate entry" in err_msg:
                raise HTTPException(
                    status_code=409,
                    detail="email already exists (%s)" % email,
                )
            else:
                # return False, "unknown error adding user"
                raise HTTPException(
                    status_code=409,
                    detail="unknown error adding user",
                )

    def find_by_id(self, user_id: int):
        user = self._session.query(User).filter(User.id == user_id).first()
        return user

    def fint_by_uuid(self, user_uuid: str):
        user = self._session.query(User).filter(User.uuid == user_uuid).first()
        return user

    def find_by_email(self, email: str):
        user = self._session.query(User).filter(User.email == email).first()
        return user

    def update_key_by_email(self, email: str, new_key: str):
        self._session.query(User).filter(User.email == email).update({"key": new_key})
        self._session.commit()
