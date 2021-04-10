from fastapi.testclient import TestClient

from main import APP

client = TestClient(APP)


def test__GET_pokemon_empty():
    response = client.get("/pokemon")

    assert response.status_code == 404
    assert response.json()["detail"] == "Not Found"


def test__GET_pokemon__not_a_pokemon(mock_network):
    response = client.get("/pokemon/not_a_pokemon")

    assert response.status_code == 404
    assert response.json()["detail"] == (
        f"`not_a_pokemon` could not be found in national pokedex, send a "
        "live specimen if this is a mistake."
    )


def test__GET_pokemon__bulbasaur(mock_network):
    response = client.get("/pokemon/bulbasaur")

    assert response.status_code == 200
    assert response.json()["description"] == (
        "Thither is a seed on its back. By soaking up the travelling lamp’s "
        "rays, the seed."
    )
    assert response.json()["name"] == "bulbasaur"


def test__GET_pokemon__bulbasaur__as_text(mock_network):
    response = client.get("/pokemon/bulbasaur?output_format=text")

    assert response.status_code == 200
    assert response.text == (
        "bulbasaur: "
        "Thither is a seed on its back. By soaking up the travelling lamp’s "
        "rays, the seed."
    )


def test__GET_pokemon__charizard(mock_network):
    response = client.get("/pokemon/charizard")

    assert response.status_code == 200
    assert response.json()["description"] == (
        "Charizard flies around the sky in search of powerful opponents. "
        "It breathes fire of such most heat it mealt stone."
    )
    assert response.json()["name"] == "charizard"

def test__GET_pokemon__charizard__as_text(mock_network):
    response = client.get("/pokemon/charizard?output_format=text")

    assert response.status_code == 200
    assert response.text == (
        "charizard: "
        "Charizard flies around the sky in search of powerful opponents. "
        "It breathes fire of such most heat it mealt stone."
    )
