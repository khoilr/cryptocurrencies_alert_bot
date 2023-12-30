from database import session
from database.models.models.user import User as UserDTO


class User:
    @staticmethod
    def upsert(**kwargs) -> UserDTO:
        user = UserDTO(**kwargs)
        session.merge(user)
        session.commit()
        return user

    # insert or update
    @staticmethod
    def insert(**kwargs) -> UserDTO:
        user = UserDTO(**kwargs)
        session.add(user)
        session.commit()
        return user

    @staticmethod
    def select_one(**kwargs) -> UserDTO:
        return session.query(UserDTO).filter_by(**kwargs).first()

    @staticmethod
    def select_multiple(**kwargs) -> list[UserDTO]:
        return session.query(UserDTO).filter_by(**kwargs).all()
