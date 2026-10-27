import datetime as dt


class InvalidStartDateError(ValueError):
    def __init__(self, start_date: dt.datetime, end_date: dt.datetime):
        super().__init__(f"start_date:{start_date} can not be greater than end_date:{end_date}")


class ModerationDecisionNotFoundError(Exception):
    def __init__(self, message: str)-> None:
        super().__init__(message)
        self.message = message


class ModerationDecisionClientInternalError(Exception):
    def __init__(self, message: str)-> None:
        super().__init__(message)
        self.message = message


class ModerationDecisionClientExternalError(Exception):
    def __init__(self, message: str)-> None:
        super().__init__(message)
        self.message = message


