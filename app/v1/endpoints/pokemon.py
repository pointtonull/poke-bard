from enum import Enum
from typing import Optional
import logging

from fastapi import APIRouter, HTTPException
from doglessdata import DataDogMetrics

import controller

ROUTER = APIRouter()


class OutputFormat(str, Enum):
    text = "text"
    json = "json"

class PokemonDescription(Enum):
    name: str
    description: str

metrics = DataDogMetrics(global_tags=["api"])
logger = logging.getLogger(__name__)


@metrics.timeit
@ROUTER.get("/pokemon/{pokemon_id}")
async def get_pokemon_description(
    pokemon_id: str, output_format: Optional[OutputFormat] = OutputFormat.json
) -> PokemonDescription:
    """
    Get Pokemon description, in proper bard style.

    It can be a pokemon name, or it's order id in National Pokedex.

    The name is case insensitive.
    """
    pokemon_id = pokemon_id.lower()
    try:
        name, description = controller.get_pokemon_description_translated(pokemon_id)
    except controller.PokemonNotFoundError as error:
        raise HTTPException(status_code=404, detail=str(error))

    if output_format == OutputFormat.text:
        response = f"{name}: {description}"
    elif output_format == OutputFormat.json:
        response = {
            "name": name,
            "description": description,
        }
    else:
        raise HTTPException(status_code=406, detail="Unsupported output format")
    return response

