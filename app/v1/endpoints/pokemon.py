from enum import Enum
from typing import Optional

from fastapi import APIRouter, HTTPException

import controller

ROUTER = APIRouter()


class OutputFormat(str, Enum):
    text = "text"
    json = "json"



@ROUTER.get("/pokemon/{pokemon_id}")
def get_pokemon_description(
    pokemon_id: str, output_format: Optional[OutputFormat] = OutputFormat.json
):
    """
    Get Pokemon description, in proper bard style.

    It can be a pokemon name, or it's order id in National Pokedex.

    The name is case insensitive.
    """
    pokemon_id = pokemon_id.lower()
    try:
        description = controller.get_pokemon_description_translated(pokemon_id)
    except controller.PokemonNotFoundError as error:
        raise HTTPException(status_code=404, detail=str(error))

    if output_format == OutputFormat.text:
        response = description
    elif output_format == OutputFormat.json:
        response = {
            "description": description,
        }
    else:
        raise RuntimeError("Unsupported output format")
    return response

