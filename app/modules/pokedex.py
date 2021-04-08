import re

import pokepy

POKEDEX = pokepy.V2Client()


TRANSFORMS = [
    (re.compile(r"\n"), r" "),
    (re.compile(r"\f"), r" "),
    (re.compile(r"  "), r" "),
]

def clean_description(description: str) -> str:
    """
    Some text that is available in pokeapi has been stripped from Games .dat
    and ROM images.

    These records are often kept as found without any non-printable characters
    beign stripped, or including out-of-context screen control characters.

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
    pokemon = POKEDEX.get_pokemon_species(pokemon_id)
    description = max(
        (
            entry.flavor_text
            for entry in pokemon.flavor_text_entries
            if entry.language.name == "en"
        ),
        key=len,
    )
    description = clean_description(description)
    return description

