from pathlib import Path

from pydantic import BaseSettings


class Settings(BaseSettings):
    geo_api: str | None = None

    class Config:
        env_file = Path(__file__).parent.parent.parent / '.env'

