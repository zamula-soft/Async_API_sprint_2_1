from datetime import datetime

from dateutil.parser import parse
from pydantic import BaseModel, Field, validator


class DateTimeMixin(BaseModel):
    created: datetime | None = Field(datetime.now(), alias='creation_date')
    modified: datetime = Field(None, alias='updated_at')

    @validator('created', 'modified', pre=True)
    def parse_dates(cls, date):
        date = date or datetime.now()
        if type(date) == str:
            return parse(date)
        elif type(date) == datetime:
            return date
        raise TypeError('date must be of type datetime or str')
