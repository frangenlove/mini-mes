from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8")

    app_name: str = "Mini-MES"
    debug: bool = False
    database_url:str = "postgresql+psycopg://mes:mes@localhost:5432/mini_mes"

settings = Settings()