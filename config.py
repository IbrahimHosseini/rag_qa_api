from pydantic import ConfigDict
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    EMBEDDING_MODEL: str = "text-embedding-3-small"
    EMBEDDING_DIMENSION: int = 1536

    OPENAI_API_KEY: str

    model_config = ConfigDict(env_file = ".env.local")

settings = Settings()