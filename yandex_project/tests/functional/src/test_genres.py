from http import HTTPStatus
import json

import pytest

from functional.testdata import genres


@pytest.mark.asyncio
async def test_get_all_genres(create_index, make_get_request):
    response = await make_get_request("/genres")

    assert response.status == HTTPStatus.OK
    result = response.body['result']
    assert len(result) == 3


@pytest.mark.asyncio
async def test_get_genre_by_id(create_index, make_get_request):
    for genre in genres:
        genre_id = genre["id"]
        response = await make_get_request(f"/genres/{genre_id}")
        assert response.status == HTTPStatus.OK
        assert response.body["id"] == genre_id
        assert response.body["name"] == genre["name"]


@pytest.mark.asyncio
async def test_person_detailed(create_index, make_get_request, redis_client):
    genre = genres[0]
    genre_id = genre["id"]
    response = await make_get_request(f"/genres/{genre_id}")

    assert response.status == HTTPStatus.OK
    assert response.body["id"] == genre["id"]
    assert response.body["name"] == genre["name"]

    genres_from_cache = redis_client.get(f'api_cache::elastic::genres::{genre_id}')
    genres_from_cache = json.loads(genres_from_cache.decode('utf-8'))

    assert genre_id == genres_from_cache['id']


@pytest.mark.asyncio
async def test_get_film_by_genre(create_index, make_get_request):
    genre = genres[1]
    genre_id = genre["id"]
    response = await make_get_request(f"/genres/{genre_id}/films/", params={})

    assert response.status == HTTPStatus.OK
    result = response.body['result']
    assert len(result) == 1
    assert (genre in result[0]['genres']) == True