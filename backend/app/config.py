from pydantic_settings import BaseSettings, SettingsConfigDict
from typing import Optional

class Settings(BaseSettings):
    PROJECT_NAME: str = "Paytm VyapaarAI"
    VERSION: str = "1.0.0"
    API_V1_STR: str = "/api/v1"
    
    DATABASE_URL: str = "sqlite+aiosqlite:///./vyapaar.db"
    GROQ_API_KEY: Optional[str] = None
    BASE_URL: str = "http://127.0.0.1:8000"
    ENVIRONMENT: str = "development"
    
    # Soundbox Demo Defaults
    DEFAULT_MERCHANT_ID: str = "sharma-kirana-001"
    DEFAULT_SOUNDBOX_ID: str = "SB-DELHI-981"

    model_config = SettingsConfigDict(env_file=".env", extra="allow")

settings = Settings()
