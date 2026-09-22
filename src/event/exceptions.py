import datetime as dt


class InvalidStartDateError(ValueError):
    def __init__(self, start_date: dt.datetime, end_date: dt.datetime):
        super().__init__(f"start_date:{start_date} can not be greater than end_date:{end_date}")



