from database import session
from database.models.dto.alert import Alert as AlertDTO


class Alert:
    @staticmethod
    def insert(**kwargs) -> AlertDTO:
        alert = AlertDTO(**kwargs)
        session.add(alert)
        session.commit()
        return alert
