from pathlib import Path

from pydantic import BaseSettings


class Settings(BaseSettings):
    tg_token: str | None = None
    api_host = str = '127.0.0.1'
    api_port = int = 8000

    class Config:
        env_file = Path(__file__).parent.parent.parent / '.env'

    @property
    def api_url(self):
        return f'http://{self.api_host}:{self.api_port}/get-nearest/'
