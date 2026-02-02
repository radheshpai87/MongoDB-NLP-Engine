import os
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    MONGODB_URL: str = os.getenv("MONGODB_URL", "mongodb://localhost:27017")
    DATABASE_NAME: str = "myapp"
    
settings = Settings()
