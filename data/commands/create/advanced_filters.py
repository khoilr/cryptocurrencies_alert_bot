from typing import Optional, Union

from telegram import Message
from telegram.ext._utils.types import FilterDataDict
from telegram.ext.filters import MessageFilter


class PositiveNumberFilter(MessageFilter):
    def filter(self, message: Message) -> Optional[Union[bool, FilterDataDict]]:
        message_text = message.text

        try:
            value = float(message_text)
            return value >= 0
        except ValueError:
            return False


class TwoPositiveNumbersFilter(MessageFilter):
    def filter(self, message: Message) -> Optional[Union[bool, FilterDataDict]]:
        text = message.text
        values = text.split(",")

        if len(values) != 2:
            return False

        try:
            value1, value2 = map(float, values)

            if value1 < 0 or value2 < 0:
                return False

            if value1 >= value2:
                return False

        except ValueError:
            return False

        return True


class PercentageOrPositiveNumberFilter(MessageFilter):
    def filter(self, message: Message) -> Optional[Union[bool, FilterDataDict]]:
        text = message.text

        if text.endswith("%"):
            text = text[:-1]

        try:
            value = float(text)
            if value < 0:
                return False
        except ValueError:
            return False

        return True


positive_number = PositiveNumberFilter()
two_positive_numbers = TwoPositiveNumbersFilter()
percentage_or_positive_number = PercentageOrPositiveNumberFilter()
