import re

import pokepy

from . import shakespeare

POKEDEX = pokepy.V2Client()
TRANSFORMS = [
    (re.compile(r"\n"), r" "),
    (re.compile(r"\f"), r" "),
    (re.compile(r"  "), r" "),
]


class PokemonNotFoundError(ValueError):
    pass


def _clean_description(description: str) -> str:
    """
    Some text that is available in pokeapi has been stripped from Games .dat
    and ROM images, without data cleaning. This mean the original non-printable
    screen control characters are kept in many cases.

    This function takes a description and returns a version with these
    characters removed.
    """
    description = description.strip()
    for pattern, replacement in TRANSFORMS:
        description = pattern.sub(replacement, description)
    return description


def get_pokemon_description(pokemon_id: str) -> str:
    """
    Queries pokeapi in search of descriptions for the given pokemon.
    If several descriptions are available it'll return the longest one.
    """
    try:
        pokemon = POKEDEX.get_pokemon_species(pokemon_id)
    except Exception as error:
        if error.status_code == 404:
            raise PokemonNotFoundError(
                f"`{pokemon_id}` could not be found in national pokedex, send "
                "a live specimen if this is a mistake."
            )
    description = max(
        (
            entry.flavor_text
            for entry in pokemon.flavor_text_entries
            if entry.language.name == "en"
        ),
        key=len,
    )
    description = _clean_description(description)
    name = pokemon.name
    return name, description
