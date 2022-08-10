from elasticsearch import AsyncElasticsearch


class Service:
    """Service for get data from elasticsearch."""

    def __init__(self, elastic: AsyncElasticsearch) -> None:
        """
        Init.
        :param elastic: connect to Elasticsearch
        """
        self.elastic = elastic
