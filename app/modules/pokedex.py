import pokepy

POKEDEX = pokepy.V2Client()


def get_pokemon_description(pokemon_id):
    pokemon = POKEDEX.get_pokemon_species(pokemon_id)
    description = max(
        (
            entry.flavor_text
            for entry in pokemon.flavor_text_entries
            if entry.language.name == "en"
        ),
        key=len,
    )
    return description

