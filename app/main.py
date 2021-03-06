import os
import logging

from doglessdata import DataDogMetrics
from fastapi import FastAPI, responses, status
from mangum import Mangum

from v1.routers import router


STAGE = os.environ.get("STAGE", "dev")
LAMBDA = "AWS_LAMBDA_FUNCTION_VERSION" in os.environ
DEBUG = STAGE == "dev"
ROOT_PATH = f"/{STAGE}" if LAMBDA else ""

APP = FastAPI(
    title="OpenBard",
    description=(
        "API Service that provides Shakespearean versions of pokemons' descriptions.\n\n"
        "If there are several descriptions available (from multiple sources), "
        "it'll use the longest available description. "
        "I am well aware of incosistencies in `sword` and `diamond` with cherries and HP; "
        "but this pokedex is just for fun. "
    ),
    root_path=ROOT_PATH,
    debug=DEBUG,
)
APP.include_router(router)

metrics = DataDogMetrics(global_tags=["api"])
logger = logging.getLogger(__name__)


@metrics.timeit
@APP.get("/")
async def get_root():
    return responses.RedirectResponse(
        f"{ROOT_PATH}/docs", status_code=status.HTTP_301_MOVED_PERMANENTLY
    )


lambda_handler = Mangum(app=APP)
