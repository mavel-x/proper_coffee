from pathlib import Path
from pydantic import BaseSettings, root_validator
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
    data_dir = Path(__file__).parent.parent / 'data'

    class Config:
        env_file = Path(__file__).parent.parent.parent / '.env'

    @root_validator
    def check_postgres_credentials(cls, values):
        if values.get('db_type') == DatabaseType.PROD:
            if not all((values.get('postgres_user'), values.get('postgres_password'))):
                raise ValueError('Missing Postgres credentials. '
                                 'Set DB_TYPE to "sqlite" if you do not want to use Postgres.')
        return values

    @property
    def database_url(self) -> str:
        if self.db_type == DatabaseType.PROD:
            return (f"postgresql://{self.postgres_user}:{self.postgres_password}"
                    f"@{self.postgres_host}:{self.postgres_port}/{self.postgres_db}")
        elif self.db_type == DatabaseType.SQLITE:
            database_path = self.data_dir / 'test.sqlite3'
            return f'sqlite:///{database_path}'
