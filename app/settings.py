from pydantic import BaseSettings


class Settings(BaseSettings):
    geo_api: str = None

    class Config:
        env_file = '.env'
