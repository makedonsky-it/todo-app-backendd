from dataclasses import dataclass


@dataclass(frozen=True)
class Settings:
    database_url: str
    cors_origins: list[str]


def get_settings() -> Settings:
    return Settings(
        database_url="postgresql+psycopg://postgres:admin@127.0.0.1:15432/postgres",
        cors_origins=["http://localhost:3000"]
    )
