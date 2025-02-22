from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=Path(__file__).parents[2] / ".env", extra="ignore")

    data_dir: Path = Path(__file__).parents[1] / "data"
    geoapify_api_key: str | None = None
    db_url: str
