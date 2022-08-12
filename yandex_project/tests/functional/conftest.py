import asyncio
from dataclasses import dataclass

import aiohttp
import pytest
import redis
from elasticsearch import AsyncElasticsearch
from multidict import CIMultiDictProxy

from functional.core import TestSettings


settings = TestSettings()


@dataclass
class HTTPResponse:
    body: dict
    headers: CIMultiDictProxy[str]
    status: int


@pytest.fixture
def make_get_request(session):
    async def inner(method: str, params: dict = None) -> HTTPResponse:
        params = params or {}
        url = 'http://fastapi:8010/api/v1' + method
        async with session.get(url, params=params) as response:
            return HTTPResponse(
                body=await response.json(),
                headers=response.headers,
                status=response.status,
            )

    return inner


@pytest.fixture(scope="session")
def event_loop():
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


@pytest.fixture(scope="session")
async def session(event_loop):
    session = aiohttp.ClientSession()
    yield session
    await session.close()


@pytest.fixture(scope="session")
def redis_client():
    return redis.Redis(
        settings.redis_host, int(settings.redis_port)
    )  # type: ignore


@pytest.fixture(scope="session", autouse=True)
async def es_client():
    client = AsyncElasticsearch(
        hosts=f"{settings.elastic_host}:{settings.elastic_port}"
    )
    yield client
    await client.close()


@pytest.fixture(scope='session')
async def create_index(es_client, type_model):
    """Create and delete films indexes"""

    name_index, structure_index, data = type_model

    if await es_client.indices.exists(index=name_index):
        await es_client.indices.delete(index=name_index)
    await es_client.indices.create(index=name_index, body=structure_index)

    create_actions = []
    delete_actions = []

    for item in data:
        delete_actions.append(
            {
                'delete': {
                    '_index': name_index,
                    '_id': item['id'],
                }
            }
        )
        create_actions.extend(
            (
                {
                    'index': {
                        '_index': name_index,
                        '_id': item['id']
                    }
                },
                item,
            )
        )

    await es_client.bulk(create_actions, refresh='true')
    yield 'create tests data'
    await es_client.bulk(delete_actions, refresh='true')
