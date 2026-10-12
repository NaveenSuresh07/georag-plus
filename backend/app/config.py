from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    DATABASE_URL: str = "postgresql+psycopg2://georag:georagpassword@localhost:5432/georag"
    
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

settings = Settings()