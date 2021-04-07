from enum import Enum
from typing import Optional

from fastapi import APIRouter

from modules.pokedex import get_pokemon_description

ROUTER = APIRouter()


class OutputFormat(str, Enum):
    text = "text"
    json = "json"
    csv = "csv"



@ROUTER.get("/pokemon/{pokemon_id}")
def get_pokemon(
    pokemon_id: str, output_format: Optional[OutputFormat] = OutputFormat.text
):
    """
    Get Pokemon description, in proper bard style.
    """
    description = get_pokemon_description(pokemon_id)
    response = {
        "description": description,
    }
    return response

