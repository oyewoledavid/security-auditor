from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    DATABASE_URL: str
    AWS_REGION: str = "us-east-1"
    API_KEY: str

    model_config = SettingsConfigDict(
        env_file=".env",
        extra="ignore"  
    )

settings = Settings()