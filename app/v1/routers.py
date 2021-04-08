from fastapi import APIRouter
from .endpoints import pokemon

router = APIRouter()

router.include_router(pokemon.ROUTER, tags=["pokemon"])
