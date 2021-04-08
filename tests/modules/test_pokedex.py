from pytest import fixture

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


@fixture(params=CLEAN_DESCRIPTION_CASES)
def clean_description_case(request):
    return request.param


def test__clean_description__cases(clean_description_case):
    original_description = clean_description_case["original_description"]
    answer = clean_description_case["answer"]

    result = pokedex.clean_description(original_description)

    assert result == answer
