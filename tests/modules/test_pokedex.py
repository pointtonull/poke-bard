import json

from pytest import fixture, raises

from modules import pokedex

CLEAN_DESCRIPTION_CASES = [
    {
        "original_description": (
            "There is a seed on its back."
            "\fBy soaking up the sun’s rays, the seed..."
        ),
        "answer": (
            "There is a seed on its back. "
            "By soaking up the sun’s rays, the seed..."
        ),
    },
    {
        "original_description": (
            "BULBASAUR can be seen napping in" "\nbright sunlight."
        ),
        "answer": ("BULBASAUR can be seen napping in bright sunlight."),
    },
    {
        "original_description": (
            "BULBASAUR can be seen napping in"
            "\nbright sunlight."
            "\nThere is a seed on its back."
            "\fBy soaking up the sun’s rays, the seed"
            "\ngrows progressively larger."
        ),
        "answer": (
            "BULBASAUR can be seen napping in bright sunlight. "
            "There is a seed on its back. "
            "By soaking up the sun’s rays, "
            "the seed grows progressively larger."
        ),
    },
]

@fixture(params=CLEAN_DESCRIPTION_CASES)
def clean_description_case(request):
    return request.param


def test__clean_description__cases(clean_description_case):
    original_description = clean_description_case["original_description"]
    answer = clean_description_case["answer"]

    result = pokedex._clean_description(original_description)

    assert result == answer


def test_get_pokemon_description__success(mock_network):
    result = pokedex.get_pokemon_description("1")

    assert result == "A strange seed was planted on its back at birth."
    assert mock_network.call_count == 1

    result = pokedex.get_pokemon_description("bulbasaur")

    assert result == "A strange seed was planted on its back at birth."
    assert mock_network.call_count == 2


def test_get_pokemon_description__not_a_pokemon(mock_network):
    with raises(pokedex.PokemonNotFoundError) as error:
        result = pokedex.get_pokemon_description("not_a_pokemon")
