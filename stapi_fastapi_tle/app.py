from importlib.metadata import version

from fastapi import FastAPI
from pydantic_settings import BaseSettings


class AppSettings(BaseSettings):
    debug: bool = False
    title: str = "Sensor Tasking API TLE Demo"
    version: str = version(__package__)


def factory(settings: AppSettings | None = None):
    settings = settings or AppSettings()
    app = FastAPI(debug=settings.debug, title=settings.title)
    return app
