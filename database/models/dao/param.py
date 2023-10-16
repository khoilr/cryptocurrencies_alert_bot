from database import session
from database.models.dto.param import Param as ParamDTO


class Param:
    @staticmethod
    def insert(**kwargs) -> ParamDTO:
        param = AlertDTO(**kwargs)
        session.add(param)
        session.commit()
        return param
