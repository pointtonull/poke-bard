from fastapi.testclient import TestClient

from main import APP

client = TestClient(APP)


def test__get_pokemon_empty():
    response = client.get("/pokemon")

    assert response.status_code == 404
    assert response.json()["detail"] == "Not Found"
