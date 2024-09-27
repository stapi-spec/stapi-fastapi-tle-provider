from importlib.metadata import version

from fastapi import FastAPI
from pydantic_settings import BaseSettings

from stapi_fastapi_tle.service.router import StapiTleRouter


class AppSettings(BaseSettings):
    debug: bool = False
    title: str = "Sensor Tasking API TLE Demo"
    version: str = version(__package__.split(".")[0])


def factory(settings: AppSettings | None = None):
    settings = settings or AppSettings()
    app = FastAPI(debug=settings.debug, title=settings.title)
    router = StapiTleRouter()
    app.include_router(router.router)
    return app
