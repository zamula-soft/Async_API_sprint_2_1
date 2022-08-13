from pydantic import BaseModel
from fastapi import Query


class Paginator:
    def __init__(
            self,
            page_size: int = Query(
                default=20,
                gt=0,
                title="Page size",
                description="Number of posts per page.",
                alias="page[size]"),
            page_number: int = Query(
                default=1,
                gt=0,
                title="Page number",
                description="Pagination page number.",
                alias="page[number]"
            )
    ):
        self.page_size = page_size
        self.page_number = page_number
