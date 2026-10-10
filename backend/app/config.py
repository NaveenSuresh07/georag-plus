from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    postgres_user: str = "georag"
    postgres_password: str = "georag_dev_pw"
    postgres_db: str = "georag"
    postgres_host: str = "localhost"
    postgres_port: int = 5432

    model_config = SettingsConfigDict(env_file="../.env", extra="ignore")

    @property
    def db_url(self) -> str:
        return (f"postgresql+psycopg://{self.postgres_user}:{self.postgres_password}"
                f"@{self.postgres_host}:{self.postgres_port}/{self.postgres_db}")

settings = Settings()