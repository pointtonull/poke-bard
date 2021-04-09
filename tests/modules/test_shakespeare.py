import json
import urllib

from pytest import fixture, raises

from modules import shakespeare

SHAKESPEAREAN_TRANSLATION_CASES = {
    "There is a seed on its back. By soaking up the sun’s rays, the seed...": "Thither is a seed on its back. By soaking up the travelling lamp’s rays,  the seed.",
    "BULBASAUR can be seen napping in bright sunlight.": "Bulbasaur can beest seen napping in bright sunlight.",
}

SHAKESPEAREAN_API_CASES = [{"data": {}, "response": {}}]


@fixture(params=SHAKESPEAREAN_TRANSLATION_CASES)
def shakespeareean_translation_cases(request):
    original_description = request.param
    answer = SHAKESPEAREAN_TRANSLATION_CASES[original_description]
    return {"original_description": original_description, "answer": answer}


@fixture
def mock_shakespeare(requests_mock):
    def callback(request, context):
        """simple shakespeare POST handler"""
        text = request.text
        text = text[len("text=") :]
        text = urllib.parse.unquote_plus(text)
        translated = SHAKESPEAREAN_TRANSLATION_CASES[text]
        response = json.dumps({"contents": {"translated": translated}})
        return response

    requests_mock.post(
        "https://api.funtranslations.com/translate/shakespeare.json",
        text=callback,
    )
    requests_mock.get(
        "https://pokeapi.co/api/v2/pokemon-species/not_a_pokemon",
        text="Not Found",
        status_code=404,
    )
    return requests_mock


def test__shakesperean_translation__cases(
    shakespeareean_translation_cases, mock_shakespeare
):
    original_description = shakespeareean_translation_cases[
        "original_description"
    ]
    answer = shakespeareean_translation_cases["answer"]

    result = shakespeare.get_shakesperean_translation(original_description)

    assert result == answer
    assert mock_shakespeare.call_count == 1

    result = shakespeare.get_shakesperean_translation(original_description)

    assert mock_shakespeare.call_count == 1
