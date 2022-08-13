from http import HTTPStatus
import json

import pytest

from functional.testdata import persons


pytestmark = pytest.mark.asyncio


async def test_get_persons(create_index, make_get_request):
    response = await make_get_request('/persons')

    result = response.body['result']

    assert response.status == HTTPStatus.OK
    assert len(result) == 8


async def test_get_person_by_id(create_index, make_get_request):
    person = persons[0]
    person_id = person["id"]
    response = await make_get_request(f"/persons/{person_id}")
    assert response.status == HTTPStatus.OK
    assert response.body["id"] == person_id
    assert response.body["full_name"] == person["full_name"]


async def test_cache_person_by_id(create_index, make_get_request, redis_client):
    person = persons[0]
    person_id = person["id"]
    response = await make_get_request(f"/persons/{person_id}", params={})

    assert response.status == HTTPStatus.OK
    assert response.body["id"] == person["id"]
    assert response.body["full_name"] == person["full_name"]

    persons_from_cache = redis_client.get(f'api_cache::elastic::persons::{person_id}')
    persons_from_cache = json.loads(persons_from_cache.decode('utf-8'))

    assert person_id == persons_from_cache['id']


async def test_get_film_by_person(create_index, make_get_request):
    person = persons[0]
    person_id = person["id"]
    response = await make_get_request(f"/persons/{person_id}/films/", params={})

    assert response.status == HTTPStatus.OK
    result = response.body['result']
    assert len(result) == 1

    persons_lst = result[0]["actors"] + result[0]["writers"] + result[0]["directors"]
    assert (person['full_name'] in [person_['name'] for person_ in persons_lst]) is True
