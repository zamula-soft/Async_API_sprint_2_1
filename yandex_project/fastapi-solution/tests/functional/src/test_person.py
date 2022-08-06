import pytest
from ..testdata import person_data


async def test_get_persons():
    pass


@pytest.mark.asyncio
async def test_get_by_id(make_get_request):
    for person in person_data:
        person_id = person('id')
        # endpoint query
        response = await make_get_request(f'persons/{person_id}')
        assert response.status == 200
        assert len(response.body) == 1
        assert response.body['uuid'] == person_id
        assert response.body['full_name'] == person['full_name']
        assert response.body['roles'] == person['roles']
        assert response.body['film_work_id'] == person['film_work_id']



@pytest.mark.asyncio
async def test_get_movies_by_person(make_get_request):
    for person in person_data:
        person_id = person('id')
        # Выполнение запроса
        response = await make_get_request(f'persons/{person_id}/films')
        assert response.status == 200
        assert len(response.body) == 1
        for film in response.body['film_work_id']:
            pass



