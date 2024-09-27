from pydantic_settings import BaseSettings
from uvicorn import run

from stapi_fastapi_tle.service.app import factory


class RunSettings(BaseSettings):
    host: str = "127.0.0.1"
    port: int = 8000
    reload: bool = False


app = factory()

if __name__ == "__main__":
    settings = RunSettings()
    run(
        "stapi_fastapi_tle.__main__:app",
        host=settings.host,
        port=settings.port,
        reload=settings.reload,
    )
