from controller import get_pokemon_description_translated


def test_get_pokemon_description__success(mock_network):
    result = pokedex.get_pokemon_description_translated("1")

    assert result == "There is a seed on its back. By soaking up the sun’s rays, the seed..."
    assert mock_network.call_count == 1

    result = pokedex.get_pokemon_description_translated("bulbasaur")

    assert result[0] == "bulbasaur"
    assert result[1] == "There is a seed on its back. By soaking up the sun’s rays, the seed..."
    assert mock_network.call_count == 1
