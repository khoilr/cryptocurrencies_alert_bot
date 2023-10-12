from stream.database import Session
from stream.database.models.dto.user import User as UserDTO

session = Session()


class User:
	@staticmethod
	def insert(**kwargs) -> UserDTO:
		user = UserDTO(**kwargs)
		session.add(user)
		session.commit()
		return user

	# insert or update
	@staticmethod
	def upsert(**kwargs) -> UserDTO:
		user = UserDTO(**kwargs)
		session.merge(user)
		session.commit()
		return user
