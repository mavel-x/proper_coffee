from pathlib import Path

from pydantic import model_validator
from pydantic_settings import BaseSettings, SettingsConfigDict
from enum import Enum


class DatabaseType(Enum):
    SQLITE = 'sqlite'
    PROD = 'prod'


class Settings(BaseSettings):
    geo_api: str | None = None
    postgres_user: str | None = None
    postgres_password: str | None = None
    postgres_host: str | None = '127.0.0.1'
    postgres_port: int | None = 5432
    postgres_db: str | None = 'places'
    db_type: DatabaseType = DatabaseType.PROD
    data_dir: Path = Path(__file__).parents[1] / 'data'

    model_config = SettingsConfigDict(
        env_file=Path(__file__).parents[2] / '.env',
        extra='ignore'
    )

    @model_validator(mode='after')
    def check_postgres_credentials(self):
        if self.db_type == DatabaseType.PROD:
            if not all([self.postgres_user, self.postgres_password]):
                raise ValueError('Missing Postgres credentials. '
                                 'Set DB_TYPE to "sqlite" if you do not want to use Postgres.')
        return self

    @property
    def database_url(self) -> str:
        if self.db_type == DatabaseType.PROD:
            return (f"postgresql://{self.postgres_user}:{self.postgres_password}"
                    f"@{self.postgres_host}:{self.postgres_port}/{self.postgres_db}")
        elif self.db_type == DatabaseType.SQLITE:
            database_path = self.data_dir / 'test.sqlite3'
            return f'sqlite:///{database_path}'
