from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    db_url: str = "postgresql+psycopg2://georag:georagpassword@localhost:5432/georag"
    DATABASE_URL: str = "postgresql+psycopg2://georag:georagpassword@localhost:5432/georag"
    
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

settings = Settings()