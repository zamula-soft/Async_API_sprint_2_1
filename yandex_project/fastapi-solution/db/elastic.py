from typing import Optional
from elasticsearch import AsyncElasticsearch
from core.config import ELASTIC_HOST, ELASTIC_PORT


es: Optional[AsyncElasticsearch] = AsyncElasticsearch(
    hosts=[{'host': ELASTIC_HOST, 'port': ELASTIC_PORT}],
    use_ssl=False,
    verify_certs=False,
)


# Функция понадобится при внедрении зависимостей
async def get_elastic() -> AsyncElasticsearch:
    return es
