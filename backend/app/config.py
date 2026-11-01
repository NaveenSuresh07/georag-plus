from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    db_url: str = "postgresql+psycopg2://georag:georagpassword@localhost:5432/georag"
    DATABASE_URL: str = "postgresql+psycopg2://georag:georagpassword@localhost:5432/georag"
    
    # LLM Settings for Batch 7 AI Explainer Agent
    LLM_PROVIDER: str = "auto"              # 'auto' | 'gemini' | 'openai' | 'ollama' | 'deterministic'
    GEMINI_API_KEY: str | None = None
    OPENAI_API_KEY: str | None = None
    OLLAMA_BASE_URL: str = "http://localhost:11434"
    LLM_MODEL: str = "gemini-2.5-flash"
    
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

settings = Settings()