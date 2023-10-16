from database import session
from database.models.dto.indicator import Indicator as IndicatorDTO


class Indicator:
    @staticmethod
    def insert(**kwargs) -> IndicatorDTO:
        indicator = IndicatorDTO(**kwargs)
        session.add(indicator)
        session.commit()
        return indicator
