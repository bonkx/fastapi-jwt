from . import pytest, pytestmark


async def test_root(client):
    response = await client.get("/")

    assert response.status_code == 200
    assert response.json() == {"message": "Server is Running..."}


async def test_docs(client):
    response = await client.get("/docs")

    # 307 Temporary Redirect
    assert response.status_code == 307
