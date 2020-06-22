from enum import Enum
from typing import Dict


class TimePeriod(str, Enum):
    MONTHS = "months"
    WEEKS = "weeks"
    DAYS = "days"
    HOURS = "hours"

    # IDEA: May add the ability to query by amount using amount kwarg.

    def convert_to_period(self, amount: int = 1) -> Dict[str, int]:
        return {self.value: amount}
