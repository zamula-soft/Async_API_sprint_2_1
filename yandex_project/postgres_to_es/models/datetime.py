from datetime import datetime

from pydantic import BaseModel, Field


class DateTimeMixin(BaseModel):
    created: datetime | None = Field(datetime.now(), alias='creation_date')
    modified: datetime = Field(None, alias='updated_at')

