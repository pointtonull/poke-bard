import os

from modules import pokedex, shakespeare
from modules.dynamo_cache import Cache


TABLE_NAME = os.environ["CACHE_TABLE"]
DUMMY = os.environ.get("DUMMY", "False").lower() == "true"


@Cache(table_name=TABLE_NAME, ttl=24*60*60, dummy=DUMMY)
def get_pokemon_description_translated(pokemon_id: str) -> str:
    name, description = pokedex.get_pokemon_description(pokemon_id)
    description = shakespeare.get_shakesperean_translation(description)
    return name, description
