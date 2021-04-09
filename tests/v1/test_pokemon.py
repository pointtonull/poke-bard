from fastapi.testclient import TestClient

from main import APP

client = TestClient(APP)


def test__get_pokemon_empty():
    response = client.get("/pokemon")

    assert response.status_code == 404
    assert response.json()["detail"] == "Not Found"


def test__get_pokemon__empty(mock_network):
    response = client.get("/pokemon")

    assert response.status_code == 404
    assert response.json()["detail"] == "Not Found"


def test__get_pokemon__not_a_pokemon(mock_network):
    response = client.get("/pokemon/not_a_pokemon")

    assert response.status_code == 404
    assert response.json()["detail"] == (
        f"`not_a_pokemon` could not be found in national pokedex, send a "
        "live specimen if this is a mistake."
    )
