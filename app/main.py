import os
from fastapi import FastAPI, responses, status
from v1.routers import router
from mangum import Mangum

STAGE = os.environ.get("STAGE", "dev")
LAMBDA = "AWS_LAMBDA_FUNCTION_VERSION" in os.environ
DEBUG = STAGE == "dev"
ROOT_PATH = f"/{STAGE}" if LAMBDA else ""

app = FastAPI(
    title="OpenBard",
    description="API Service that provides Shakespearean versions of pokemons' descriptions.",
    root_path=ROOT_PATH,
    debug=DEBUG,
)
app.include_router(router)


@app.get("/")
async def get_root():
    return responses.RedirectResponse(
        f"{ROOT_PATH}/docs", status_code=status.HTTP_301_MOVED_PERMANENTLY
    )


lambda_handler = Mangum(app=app)