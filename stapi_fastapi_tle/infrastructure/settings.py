from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict

MOCK_TLE = (
    "1 99999U 24001A   24001.50000000  .00001103  00000-0  33518-4 0  9998\n"
    "2 99999 90.00000   0.7036 0003481 300.0000   0.3331 15.07816962  1770"
)


class TleSettings(BaseSettings):
    src: str = MOCK_TLE

    model_config = SettingsConfigDict(env_prefix="tle_")

    @classmethod
    @lru_cache
    def load(cls):
        return cls()
