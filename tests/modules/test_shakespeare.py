import json
import urllib

from pytest import fixture, raises

from modules import shakespeare
from conftest import SHAKESPEAREAN_TRANSLATION_CASES


@fixture(params=SHAKESPEAREAN_TRANSLATION_CASES)
def shakespeareean_translation_cases(request):
    original_description = request.param
    answer = SHAKESPEAREAN_TRANSLATION_CASES[original_description]
    return {"original_description": original_description, "answer": answer}


def test__shakesperean_translation__cases(
    shakespeareean_translation_cases, mock_network
):
    original_description = shakespeareean_translation_cases[
        "original_description"
    ]
    answer = shakespeareean_translation_cases["answer"]

    result = shakespeare.get_shakesperean_translation(original_description)

    assert result == answer
    assert mock_network.call_count == 1

    result = shakespeare.get_shakesperean_translation(original_description)

    assert mock_network.call_count == 2
