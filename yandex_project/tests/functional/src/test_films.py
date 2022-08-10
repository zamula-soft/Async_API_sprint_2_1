from http import HTTPStatus
import json

import pytest

from functional.testdata import movies, movies_index


@pytest.fixture(scope='session')
async def create_index(es_client):
    """Create and delete films indexes"""
    await es_client.indices.delete(index='movies')
    await es_client.indices.create(index='movies', body=movies_index)

    create_actions = []
    delete_actions = []

    for film in movies:
        delete_actions.append(
            {
                'delete': {
                    '_index': 'movies',
                    '_id': film['id'],
                }
            }
        )
        create_actions.extend(
            (
                {
                    'index': {
                        '_index': 'movies',
                        '_id': film['id']
                    }
                },
                film,
            )
        )

    await es_client.bulk(create_actions, refresh='true')
    yield 'create tests data'
    await es_client.bulk(delete_actions, refresh='true')


@pytest.mark.asyncio
async def test_film_detailed(create_index, make_get_request, redis_client):
    """Tests get film by id and test save film to cache."""
    data = movies[0]
    film_id = data['id']
    response = await make_get_request(f'/films/{film_id}', params={})

    assert response.status == HTTPStatus.OK
    assert response.body['id'] == data['id']
    assert response.body['title'] == data['title']
    assert response.body['rating'] == data['rating']
    assert response.body['genres'] == data['genres']
    assert response.body['actors'] == data['actors']
    assert response.body['writers'] == data['writers']
    assert response.body['directors'] == data['directors']

    movies_from_cache = redis_client.get(f'api_cache::elastic::movies::{film_id}')
    movies_from_cache = json.loads(movies_from_cache.decode('utf-8'))

    assert film_id == movies_from_cache['id']


@pytest.mark.asyncio
async def test_get_film(make_get_request):
    """Tests wrong get film with wrong id."""
    response = await make_get_request('/films/unknown')

    assert response.status == HTTPStatus.NOT_FOUND
    assert response.body['detail'] == 'film with uuid unknown not found.'


@pytest.mark.asyncio
async def test_get_films(make_get_request):
    """Tests get all films."""
    response = await make_get_request('/films')

    result = response.body['result']

    assert response.status == HTTPStatus.OK
    assert len(result) == 3


@pytest.mark.asyncio
async def test_get_films_pagination(make_get_request):
    """Tests work pagination."""
    params = {'page[size]': 1}
    response = await make_get_request('/films', params=params)

    result = response.body['result']

    assert response.status == HTTPStatus.OK
    assert len(result) == 1
    assert response.body['pagination']['last'] == 2


@pytest.mark.asyncio
async def test_get_films_order(make_get_request):
    """Tests work ordering."""
    params = {'page[size]': 1, 'sort': 'rating'}
    response = await make_get_request('/films', params=params)

    result = response.body['result']

    data = movies[2]

    assert response.status == HTTPStatus.OK
    assert len(result) == 1
    assert result[0]['rating'] == data['rating']
