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
            "There is a seed on its back. By soaking up the sun’s rays, the seed..."
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
            "By soaking up the sun’s rays, the seed grows progressively larger."
        ),
    },
]

BODY_1 = {
    "flavor_text_entries": [
        {
            "flavor_text": "A strange seed was\nplanted on its\nback at birth.",
            "language": {
                "name": "en",
            },
        },
        {
            "flavor_text": "It can go for days\nwithout eating.",
            "language": {
                "name": "en",
            },
        },
    ],
}



@fixture(params=CLEAN_DESCRIPTION_CASES)
def clean_description_case(request):
    return request.param


def test__clean_description__cases(clean_description_case):
    original_description = clean_description_case["original_description"]
    answer = clean_description_case["answer"]

    result = pokedex._clean_description(original_description)

    assert result == answer


@fixture
def mock_pokeapi(requests_mock):
    requests_mock.get(
        "https://pokeapi.co/api/v2/pokemon-species/1", text=json.dumps(BODY_1)
    )
    requests_mock.get(
        "https://pokeapi.co/api/v2/pokemon-species/bulbasaur", text=json.dumps(BODY_1)
    )
    requests_mock.get(
        "https://pokeapi.co/api/v2/pokemon-species/not_a_pokemon",
        text="Not Found",
        status_code=404,
    )
    return requests_mock


def test_get_pokemon_description__success(mock_pokeapi):
    result = pokedex.get_pokemon_description("1")

    assert result == "A strange seed was planted on its back at birth."
    assert mock_pokeapi.call_count == 1

    result = pokedex.get_pokemon_description("bulbasaur")

    assert result == "A strange seed was planted on its back at birth."
    assert mock_pokeapi.call_count == 2


def test_get_pokemon_description__not_a_pokemon(mock_pokeapi):
    with raises(pokedex.PokemonNotFoundError) as error:
        result = pokedex.get_pokemon_description("not_a_pokemon")
