from functools import lru_cache

import requests


@lru_cache()
def get_shakesperean_translation(text: str) -> str:
    response = requests.post(
        "https://api.funtranslations.com/translate/shakespeare.json",
        data={"text": text},
    )
    translated = response.json()["contents"]["translated"]
    return translated
