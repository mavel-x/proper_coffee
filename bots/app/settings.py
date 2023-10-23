from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    tg_token: str | None = None
    api_host: str = '127.0.0.1'
    api_port: int = 8000

    model_config = SettingsConfigDict(
        env_file=Path(__file__).parents[2] / '.env',
        extra='ignore'
    )

    @property
    def api_url(self):
        return f'http://{self.api_host}:{self.api_port}/get-nearest/'
