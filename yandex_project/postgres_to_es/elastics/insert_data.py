from elasticsearch import Elasticsearch, helpers
import backoff

from settings import ElascticSearchDsl


FIELDS = [
    'id',
    'rating',
    'genre',
    'title',
    'description',
    'directors_names',
    'actors_names',
    'writers_names',
    'writers',
    'actors',
]


class ESLoader:
    """Load data to ElasticSearch."""

    def __init__(self) -> None:
        """Init."""
        self.__client = Elasticsearch(hosts=[ElascticSearchDsl().dict()])

    @backoff.on_exception(backoff.expo, BaseException, max_tries=5)
    def save_data(self, data) -> None:
        """
        Save data to ElasticSearch.

        :param data: Data for save in ElasticSearch.
        """
        self.__check_connection()
        helpers.bulk(self.__client, generate_data(data))

    @backoff.on_exception(backoff.expo, BaseException, max_tries=5)
    def __check_connection(self) -> None:
        """Check connection to ElasticSearch before save data"""
        if not self.__client.ping():
            raise ConnectionError


@backoff.on_exception(backoff.expo, BaseException, max_tries=5)
def generate_data(movies_list: list) -> dict:
    """
    Generate data in need format for ElasticSearch.

    :param movies_list: list of update movies.
    :return: data for save.
    """
    persons_fields = ['actors', 'writers']
    for movie in movies_list:
        doc = {}
        for fld_name in FIELDS:
            if fld_name in persons_fields:
                doc[fld_name] = [{'id': person['id'], 'name': person['name']} for person in movie[fld_name]]
            elif fld_name == 'directors_names' and movie[fld_name] is None:
                doc[fld_name] = []
            else:
                doc[fld_name] = movie[fld_name]

        yield {
            '_index': 'movies',
            '_id': movie['id'],
            **doc,
        }
