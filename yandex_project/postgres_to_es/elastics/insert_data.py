from elasticsearch import Elasticsearch, helpers
import backoff

from settings import ELASTICSEARCH_DSL


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
    'directors',
    'genres',
]


class ESLoader:
    """"""

    def __init__(self) -> None:
        self.__client = Elasticsearch(hosts=ELASTICSEARCH_DSL)

    def save_data(self, data) -> None:
        self.__check_connection()
        helpers.bulk(self.__client, generate_data(data))

    @backoff.on_exception(backoff.expo, BaseException)
    def __check_connection(self) -> None:
        if not self.__client.ping():
            raise ConnectionError


def generate_data(movies_list):
    persons_fields = ['actors', 'writers', 'directors', 'genres']
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