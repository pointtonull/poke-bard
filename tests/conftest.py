import json
import re
import urllib

from pytest import fixture

SHAKESPEAREAN_TRANSLATION_CASES = {
    "There is a seed on its back. By soaking up the sun’s rays, the seed...": "Thither is a seed on its back. By soaking up the travelling lamp’s rays,  the seed.",
    "BULBASAUR can be seen napping in bright sunlight.": "Bulbasaur can beest seen napping in bright sunlight.",
}

POKE_API_1 = {
    "flavor_text_entries": [
        {
            "flavor_text": (
                "There is a seed on its back. By soaking up the sun’s rays, "
                "the seed..."
            ),
            "language": {"name": "en"},
        },
        {
            "flavor_text": "It can go for days\nwithout eating.",
            "language": {"name": "en"},
        },
    ]
}


@fixture
def mock_network(requests_mock):

    # Funtranslations Server
    def shakespeare_callback(request, context):
        """simple shakespeare POST handler"""
        text = request.text
        text = text[len("text=") :]
        text = urllib.parse.unquote_plus(text)
        translated = SHAKESPEAREAN_TRANSLATION_CASES[text]
        response = json.dumps({"contents": {"translated": translated}})
        return response

    requests_mock.post(
        "https://api.funtranslations.com/translate/shakespeare.json",
        text=shakespeare_callback,
    )

    # PokeAPI Server
    requests_mock.get(
        "https://pokeapi.co/api/v2/pokemon-species/not_a_pokemon",
        text="Not Found",
        status_code=404,
    )

    requests_mock.get(
        "https://pokeapi.co/api/v2/pokemon-species/1",
        text=json.dumps(POKE_API_1),
    )
    requests_mock.get(
        "https://pokeapi.co/api/v2/pokemon-species/bulbasaur",
        text=json.dumps(POKE_API_1),
    )
    requests_mock.get(
        "https://pokeapi.co/api/v2/pokemon-species/not_a_pokemon",
        text="Not Found",
        status_code=404,
    )

    # Test Server
    requests_mock.get(re.compile(r"^http://testserver/.*"), real_http=True)

    return requests_mock
