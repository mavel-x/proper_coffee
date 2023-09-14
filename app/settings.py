from pydantic import BaseSettings


class Settings(BaseSettings):
    geo_api: str

    class Config:
        env_file = '.env'
