from .base_config import CustomBase


class Person(CustomBase):
    """Person Model"""

    id: str = None
    full_name: str = None
