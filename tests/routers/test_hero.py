# import time

import pytest


@pytest.fixture()
def payload_hero():
    """Generate a payload."""
    return {
        "id": 1,
        "name": "Tony Stark",
        "secret_name": "Iron Man",
        "age": 40,
    }


@pytest.fixture()
def payload_hero_update():
    """Generate a update payload."""
    return {
        "id": 1,
        "name": "Tony Stark Update",
        "secret_name": "Iron Man Update",
        "age": 30,
    }


@pytest.mark.anyio
async def test_create_heroes(client, api_prefix, payload_hero):
    url = f"{api_prefix}/heroes/"
    response = await client.post(url, json=payload_hero)
    data = response.json()
    print(data)

    assert response.status_code == 201
    assert data["name"] == "Tony Stark"
    assert data["secret_name"] == "Iron Man"
    assert data["age"] == 40
    assert "id" in data


@pytest.mark.anyio
async def test_create_heroes_422_exception(client, api_prefix):
    url = f"{api_prefix}/heroes/"
    response = await client.post(url, json={})
    data = response.json()
    print(data)

    assert response.status_code == 422
    assert data["detail"][0]["type"] == "missing"
    assert data["detail"][0]["msg"] == "Field required"


@pytest.mark.anyio
async def test_create_heroes_age_validation(client, api_prefix, payload_hero):
    payload = payload_hero
    # set age invalid value
    payload["age"] = -1

    url = f"{api_prefix}/heroes/"
    response = await client.post(url, json=payload)
    data = response.json()
    print(data)

    assert response.status_code == 422
    assert data["detail"][0]["type"] == "value_error"
    assert data["detail"][0]["loc"][1] == "age"
    assert data["detail"][0]["msg"] == "Value error, Invalid age"


@pytest.mark.anyio
async def test_get_hero(client, api_prefix, payload_hero):
    id = payload_hero['id']

    url = f"{api_prefix}/heroes/{id}"
    response = await client.get(url)
    data = response.json()
    print(data)

    assert response.status_code == 200
    assert data["name"] == "Tony Stark"
    assert data["secret_name"] == "Iron Man"
    assert data["age"] == 40
    assert data["id"] == id


@pytest.mark.anyio
async def test_get_hero_not_found(client, api_prefix):
    id = 2

    url = f"{api_prefix}/heroes/{id}"
    response = await client.get(url)
    data = response.json()
    print(data)

    assert response.status_code == 404
    assert data["detail"] == f"Hero with ID {id} not found"


@pytest.mark.anyio
async def test_update_hero(client, api_prefix, payload_hero_update):
    id = payload_hero_update['id']
    url = f"{api_prefix}/heroes/{id}"
    response = await client.put(url, json=payload_hero_update)
    data = response.json()
    print(data)

    assert response.status_code == 200
    assert data["name"] == "Tony Stark Update"
    assert data["secret_name"] == "Iron Man Update"
    assert data["age"] == 30
    assert data["id"] == id


@pytest.mark.anyio
async def test_update_hero_not_found(client, api_prefix, payload_hero_update):
    id = 2
    url = f"{api_prefix}/heroes/{id}"

    response = await client.put(url, json=payload_hero_update)
    data = response.json()
    print(data)

    assert response.status_code == 404
    assert data["detail"] == f"Hero with ID {id} not found"


@pytest.mark.anyio
async def test_delete_hero(client, api_prefix):
    id = 1
    url = f"{api_prefix}/heroes/{id}"

    response = await client.delete(url)

    assert response.status_code == 204
    assert response.text == ""

    # Try to get the deleted item
    response = await client.get(url)
    assert response.status_code == 404
