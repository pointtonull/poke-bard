from enum import Enum
from typing import Optional

from fastapi import APIRouter

from modules.pokedex import get_pokemon_description

ROUTER = APIRouter()


class OutputFormat(str, Enum):
    text = "text"
    json = "json"



@ROUTER.get("/pokemon/{pokemon_id}")
def get_pokemon(
    pokemon_id: str, output_format: Optional[OutputFormat] = OutputFormat.json
):
    """
    Get Pokemon description, in proper bard style.
    """
    description = get_pokemon_description(pokemon_id)
    if output_format == OutputFormat.text:
        response = description
    elif output_format == OutputFormat.json:
        response = {
            "description": description,
        }
    else:
        raise RuntimeError("Unsupported output format")
    return response

